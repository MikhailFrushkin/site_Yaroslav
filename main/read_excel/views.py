import glob
import os
from datetime import datetime

from django.shortcuts import render
from loguru import logger
import openpyxl
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from main.settings import STATIC_ROOT, STATICFILES_DIRS
from read_excel.forms import DowloadFile
from read_excel.models import Orders, GroupedOrders, MyFiles
from utils.convert import convert
from utils.utils import search_folder, split_image, unique_images_function, distribute_images


class MainPage(ListView, LoginRequiredMixin):
    login_url = 'users/login/'
    template_name = 'read_excel/main_page.html'
    model = Orders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        print(STATIC_ROOT, STATICFILES_DIRS)
        context['orders'] = Orders.objects.filter(status='Новое').values('code_prod', 'name_product', 'status',
                                                                         'path_files') \
            .annotate(total_num=Count('code_prod')).order_by('-total_num')
        context['orders_old'] = Orders.objects.exclude(status='Новое').values('code_prod', 'name_product', 'status',
                                                                              'path_files') \
            .annotate(total_num=Count('code_prod')).order_by('-total_num')
        return context


class CollectProduct(ListView, LoginRequiredMixin):
    login_url = 'users/login/'
    template_name = 'read_excel/collect.html'
    model = Orders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Q
        products = Orders.objects.filter(status='Новое').exclude(Q(path_files__isnull=True)). \
            values('code_prod', 'name_product', 'path_files', 'size', 'quantity'). \
            annotate(total_num=Count('code_prod')).order_by('-total_num')

        for prod in products:
            obj, created = GroupedOrders.objects.get_or_create(
                name_product=prod['name_product'],
                code_prod=prod['code_prod'],
                total_num=prod['total_num'],
                path_files=prod['path_files'], )

        for order in products:
            files = glob.glob(order['path_files'] + '/*.png') + glob.glob(order['path_files'] + '/*.jpg')
            if len(files) > 1:
                print('нашлось больше 1 файла со значками')
                break
            elif len(files) == 0:
                files = glob.glob(order['path_files'] + '/*.xcf')
                files = sorted(files, key=lambda f: os.path.getsize(f), reverse=True)
                name_image = convert(files[0])
            elif len(files) > 0:
                name_image = files[0]
            else:
                print(f'не нашлись файлы изображений {order["path_files"]}')
            try:
                split_image(name_image, order['path_files'], order)
            except Exception as ex:
                print(f'Ошибка в разделение изображения {ex}')
            try:
                unique_images_function(order['path_files'], order)
            except Exception as ex:
                print(f'Ошибка в разделение изображения {ex}')

        context['products'] = GroupedOrders.objects.all()
        context['bad_products'] = Orders.objects.filter(path_files__isnull=True). \
            values('code_prod', 'name_product', 'path_files'). \
            annotate(total_num=Count('code_prod')).order_by('-total_num')
        return context


class AddImages(ListView, LoginRequiredMixin):
    login_url = 'users/login/'
    template_name = 'read_excel/add_images.html'
    model = GroupedOrders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_37 = GroupedOrders.objects.filter(size=37)
        queryset_56 = GroupedOrders.objects.filter(size=56)

        context['queryset_37'] = queryset_37
        context['queryset_56'] = queryset_56
        MyFiles.objects.all().delete()
        try:
            distribute_images(queryset_37)
        except Exception as ex:
            logger.debug(f'Ошибка в добавление изображений на лист {ex}')
        # try:
        #     distribute_images(queryset_56)
        # except Exception as ex:
        #     logger.debug(f'Ошибка в добавление изображений на лист {ex}')
        context['files_37'] = MyFiles.objects.filter(size=37)
        context['files_56'] = MyFiles.objects.filter(size=56)

        return context


class Dowload(FormView, LoginRequiredMixin):
    login_url = 'users/login/'
    form_class = DowloadFile
    model = Orders
    template_name = 'read_excel/dowload.html'
    redirect_authenticated_user = ''
    success_url = reverse_lazy('read_excel:main')

    def form_valid(self, form):
        if form.cleaned_data.get('file', False):
            file = form.cleaned_data['file']
            Orders.objects.all().delete()
            GroupedOrders.objects.all().delete()

            workbook = openpyxl.load_workbook(file)
            worksheet = workbook.active
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                order = Orders(
                    number=row[0],
                    qr=row[1],
                    sticker=row[2],
                    created_at_order=datetime.strptime(row[3], '%H:%M:%S %d.%m.%Y'),
                    name_product=row[5],
                    price=row[8],
                    code_wid=row[10],
                    code_prod=row[11],
                    status=row[13],
                    duration=row[17],
                    path_files=search_folder(row[11])
                )
                order.save()
            return super().form_valid(form)


