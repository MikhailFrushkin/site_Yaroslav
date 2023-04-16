from django.urls import path

from .views import MainPage

app_name = 'read_excel'

urlpatterns = [
    path('', MainPage.as_view(), name='main'),
]
