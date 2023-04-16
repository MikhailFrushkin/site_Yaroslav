from django.urls import path

from .views import MainPage, Dowload, CollectProduct

app_name = 'read_excel'

urlpatterns = [
    path('dowload/', Dowload.as_view(), name='dowload'),
    path('collect/', CollectProduct.as_view(), name='collect'),
    path('', MainPage.as_view(), name='main'),
]
