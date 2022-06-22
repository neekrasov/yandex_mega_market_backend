from datetime import datetime

from rest_framework import serializers

from src.market.models import ShopUnit


def validate_parentId(parent_id):
    unit = ShopUnit.objects.get_unit_or_none(id=parent_id)
    if unit and (unit.type == 'OFFER' or unit == parent_id):
        raise serializers.ValidationError("failed _validate_parentId")


def validate_price(price, type):
    if type == 'OFFER' and (price is None or price < 0):
        raise serializers.ValidationError("failed _validate_price, price is none or price<0")
    if type == 'CATEGORY' and price is not None:
        raise serializers.ValidationError("failed _validate_price, price is no Null")


def validate_date(value):
    try:
        datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        raise serializers.ValidationError("failed _validate_date")


def validate_name(name, unit):
    another_unit = ShopUnit.objects.get_unit_or_none(name=name)
    unit = ShopUnit.objects.get_unit_or_none(id=unit['id'])
    if unit and unit == another_unit:
        return
    if another_unit:
        raise serializers.ValidationError('name failed')
