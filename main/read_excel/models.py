from django.db import models


class Orders(models.Model):
    number = models.IntegerField(verbose_name='Номер задания', null=True, blank=True)
    qr = models.CharField(verbose_name='QR-код поставки', max_length=30, null=True, blank=True)
    sticker = models.CharField(verbose_name='Стикер ', max_length=20, null=True, blank=True)
    created_at_order = models.DateTimeField(verbose_name='Дата создания', null=True, blank=True)
    name_product = models.TextField(verbose_name='Название товара', null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Стоимость', null=True, blank=True)
    code_wid = models.IntegerField(verbose_name='Артикул Wildberries', null=True, blank=True)
    code_prod = models.CharField(verbose_name='Артикул продавца', db_index=True, max_length=100)
    status = models.CharField(verbose_name='Статус задания', max_length=50)
    duration = models.CharField(verbose_name='Время с момента заказа', max_length=50, null=True, blank=True)

    path_files = models.TextField(verbose_name='Папка с файлами заказа', null=True, blank=True)
    size = models.IntegerField(verbose_name='Размер значка', null=True, blank=True)
    quantity = models.IntegerField(verbose_name='Количество значков в наборе', null=True, blank=True)

    created_at = models.DateTimeField(verbose_name='Время записи', auto_created=True, default='2023-01-01 00:00:00')

    class Meta:
        ordering = ('code_prod', '-created_at')
        index_together = (('code_prod',),)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.code_prod} - {self.name_product}'


class GroupedOrders(models.Model):
    name_product = models.TextField(verbose_name='Название товара', null=True, blank=True)
    code_prod = models.CharField(verbose_name='Артикул продавца', db_index=True, max_length=100)
    total_num = models.IntegerField(verbose_name='Колиество заказано')

    path_files = models.TextField(verbose_name='Папка с файлами заказа', null=True, blank=True)
    size = models.IntegerField(verbose_name='Размер значка', null=True, blank=True)
    quantity = models.IntegerField(verbose_name='Количество значков в наборе', null=True, blank=True)

    class Meta:
        ordering = ('code_prod',)
        index_together = (('code_prod',),)
        verbose_name = 'Сгруппированный заказ'
        verbose_name_plural = 'Сгруппированный заказы'

    def __str__(self):
        return f'{self.code_prod} - {self.name_product}'

