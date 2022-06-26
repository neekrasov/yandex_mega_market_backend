from django.db.models import Avg

from src.market.models import ShopUnit
from src.services.exceptions import ValidationError


def price_calculation(unit: ShopUnit):
    if unit is None:
        return

    unit.price = unit.children.all().aggregate(Avg('price'))['price__avg']
    unit.save()

    if unit.parentId:
        price_calculation(unit.parentId)
    else:
        return


def get_correct_data(data: dict) -> dict:
    updateDate = data.get('updateDate')

    # Валидация на наличие обязательного поля updateDate.
    if not updateDate:
        raise ValidationError("update date was not sent")

    items = data.get('items', [])

    # Валидация пустого списка items, дублирования id и name.
    if not items:
        raise ValidationError("items list is empty")
    else:
        duplicates = dict()
        for item in items:
            duplicates[item['id']] = duplicates.get(item['id'], 0) + 1
            if duplicates[item['id']] > 1:
                raise ValidationError("dubplicate 'id' field")
            duplicates[item['name']] = duplicates.get(item['name'], 0) + 1
            if duplicates[item['name']] > 1:
                raise ValidationError("dubplicate 'name' field")
            # Обновление даты для каждого юнита.
            item.update({'date': updateDate})
    return items
