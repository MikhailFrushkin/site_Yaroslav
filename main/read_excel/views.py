import glob
from datetime import datetime

import openpyxl
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from read_excel.forms import DowloadFile
from read_excel.models import Orders, GroupedOrders
from utils.utils import search_folder, split_image, unique_images_function


class MainPage(ListView, LoginRequiredMixin):
    login_url = 'users/login/'
    template_name = 'read_excel/main_page.html'
    model = Orders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context['products'] = Orders.objects.exclude(Q(path_files__isnull=True)). \
            values('code_prod', 'name_product', 'path_files'). \
            annotate(total_num=Count('code_prod')).order_by('-total_num')


        for prod in context['products']:
            obj, created = GroupedOrders.objects.get_or_create(
                name_product=prod['name_product'],
                code_prod=prod['code_prod'],
                total_num=prod['total_num'],
                path_files=prod['path_files'],
            )

        for order in context['products']:
            files = glob.glob(order['path_files'] + '/*.png') + glob.glob(order['path_files'] + '/*.jpg')
            if len(files) > 1:
                print('найшлось больше 1 файла со значками')
            elif len(files) > 0:
                name_image = files[0]
                split_image(name_image, order['path_files'])
                unique_images_function(order['path_files'])
            else:
                print(order)
        context['bad_products'] = Orders.objects.filter(path_files__isnull=True). \
            values('code_prod', 'name_product', 'path_files'). \
            annotate(total_num=Count('code_prod')).order_by('-total_num')

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
