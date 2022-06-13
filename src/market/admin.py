from django.contrib import admin

from ..market.models import ShopUnit


@admin.register(ShopUnit)
class ShopUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parentId', 'type', 'price', 'date')

