from django import forms

from django.utils.translation import gettext_lazy as _


class DowloadFile(forms.Form):
    file = forms.FileField(label=_('Файл выгрузки с wildberris'), required=False,
                           widget=forms.ClearableFileInput(attrs={'class': 'btn btn-sm btn-outline-secondary'}))

