from datetime import datetime

import openpyxl
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from read_excel.forms import DowloadFile
from read_excel.models import Orders
from users.forms import UserLoginForm


class MainPage(FormView, LoginRequiredMixin):
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

                )
                order.save()
            return super().form_valid(form)


