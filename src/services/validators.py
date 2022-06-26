from datetime import datetime

from src.market.models import ShopUnit
from src.services import exceptions


def validate_parentId(parent_id):
    unit = ShopUnit.objects.get_unit_or_none(id=parent_id)
    if unit and (unit.type == 'OFFER' or unit == parent_id):
        raise exceptions.ValidationError("failed parentId")


def validate_price(price, type):
    if type == 'OFFER' and (price is None or price < 0):
        raise exceptions.ValidationError("price must be >= 0")
    if type == 'CATEGORY' and price is not None:
        raise exceptions.ValidationError("price must be null")


def validate_date(value):
    try:
        date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        raise exceptions.ValidationError("date parse failed")
    return date


def validate_name(name, unit):
    another_unit = ShopUnit.objects.get_unit_or_none(name=name)
    unit = ShopUnit.objects.get_unit_or_none(id=unit['id'])
    if unit and unit == another_unit:
        return
    if another_unit:
        raise exceptions.ValidationError('unit with the same name already exists')


def validate_type(type, id):
    shop_unit = ShopUnit.objects.get_unit_or_none(id=id)
    if shop_unit.type.lower() != type:
        raise exceptions.ValidationError("when modifying an existing category, it is not possible to change its type")
    if type not in ("offer", "category"):
        raise exceptions.ValidationError("the 'type' field can only contain the following values: CATEGORY or OFFER")
