from django.db import IntegrityError
from rest_framework import serializers

from src.market.models import ShopUnit
from src.services import exceptions
from src.services.services import price_calculation
from src.services.validators import validate_parentId, validate_price, validate_date, validate_name, validate_type


class ShopUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnit
        fields = ('id', 'name', 'date', 'type', 'price', 'parentId')


class ShopUnitImportSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    date = serializers.CharField(max_length=100, required=True)
    type = serializers.CharField(required=True)
    parentId = serializers.UUIDField(allow_null=True, required=False)
    price = serializers.IntegerField(required=True, allow_null=True)

    def create(self, validated_data):
        shop_unit = ShopUnit.objects.get_unit_or_none(id=validated_data.get('id'))
        if shop_unit is not None:
            last_parent = shop_unit.parentId
            shop_unit.date = validated_data['date']
            shop_unit.name = validated_data['name']
            shop_unit.parentId = validated_data['parentId']

            if shop_unit.type.lower() == 'offer':
                shop_unit.price = validated_data['price']

            shop_unit.save()
            if last_parent is not None:
                price_calculation(last_parent)
        else:
            try:
                shop_unit = ShopUnit.objects.create(**validated_data)
            except IntegrityError:
                raise exceptions.ValidationError()
        return shop_unit

    def validate(self, unit):
        parent_id = unit.get('parentId')
        shop_unit = ShopUnit.objects.get_unit_or_none(id=unit['id'])

        if parent_id:
            unit['parentId'] = validate_parentId(parent_id)

        unit['type'] = validate_type(unit['type'], shop_unit)
        validate_price(unit['price'], unit['type'])
        validate_date(unit['date'])
        validate_name(unit['name'], shop_unit)
        return unit


class ShopUnitDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnit
        fields = ('id', 'name', 'date', 'type', 'price', 'parentId')

    def to_representation(self, unit: ShopUnit):
        return self.get_representation_data(unit)

    def get_representation_data(self, unit: ShopUnit):
        children = unit.children.all()
        representation_data = ShopUnitSerializer.to_representation(self, unit)

        if children is None:
            return ShopUnitSerializer(unit)

        if unit.type == 'CATEGORY':
            representation_data.update({'children': [self.get_representation_data(child) for child in children]})
        return representation_data
