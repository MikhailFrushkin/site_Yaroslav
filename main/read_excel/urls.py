from django.urls import path

from .views import MainPage, Dowload, CollectProduct, AddImages

app_name = 'read_excel'

urlpatterns = [
    path('dowload/', Dowload.as_view(), name='dowload'),
    path('collect/', CollectProduct.as_view(), name='collect'),
    path('add_images/', AddImages.as_view(), name='add_images'),
    path('', MainPage.as_view(), name='main'),
]
