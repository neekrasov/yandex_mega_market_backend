from datetime import datetime

from src.market.models import ShopUnit
from src.services import exceptions


def validate_parentId(parent_id):
    unit = ShopUnit.objects.get_unit_or_none(id=parent_id)
    if unit and (unit.type == 'OFFER' or unit == parent_id):
        raise exceptions.ValidationError("failed parentId")
    return unit


def validate_price(price, type):
    if type.lower() == 'offer' and (price is None or price < 0):
        raise exceptions.ValidationError("the offer price field must be >= 0")
    if type.lower() == 'category' and price is not None:
        raise exceptions.ValidationError("the category price field must be null")


def validate_date(value):
    try:
        date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        raise exceptions.ValidationError("the date format was entered incorrectly")
    return date


def validate_name(name, unit):
    another_unit = ShopUnit.objects.get_unit_or_none(name=name)
    if unit and unit == another_unit:
        return
    if another_unit:
        raise exceptions.ValidationError('unit with the same name already exists')


def validate_type(type, shop_unit):
    if shop_unit.type.lower() != type.lower():
        raise exceptions.ValidationError("when modifying a unit, you cannot change the it type")
    if type.lower() not in ("offer", "category"):
        raise exceptions.ValidationError("the 'type' field can only contain the following values: CATEGORY or OFFER")
