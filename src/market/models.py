from django.db import models

from src.market.managers import UnitManager


class ShopUnit(models.Model):
    class ShopUnitType(models.TextChoices):
        OFFER = 'OFFER', 'OFFER'
        CATEGORY = 'CATEGORY', 'CATEGORY'

    id = models.UUIDField(verbose_name='Уникальный идентификатор', primary_key=True)
    name = models.CharField(verbose_name='Имя категории/товара', max_length=100, unique=True)
    date = models.DateTimeField(verbose_name='Время последнего обновления элемента')
    type = models.CharField(verbose_name='Тип элемента - категория или товар', choices=ShopUnitType.choices,
                            max_length=8)
    price = models.IntegerField(verbose_name='Цена', null=True, blank=True)
    parentId = models.ForeignKey('self', verbose_name='UUID родительской категории', on_delete=models.CASCADE,
                                 null=True, blank=True, related_name='children')

    objects = UnitManager()

    def __str__(self):
        return f'{self.name} - {self.type}'

    class Meta:
        db_table = 'shop_unit'
