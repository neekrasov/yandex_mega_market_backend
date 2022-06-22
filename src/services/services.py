from django.db.models import Avg


def price_calculation(unit):
    if unit is None:
        return

    unit.price = unit.children.all().aggregate(Avg('price'))['price__avg']
    unit.save()

    if unit.parentId:
        price_calculation(unit.parentId)
    else:
        return

