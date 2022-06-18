import datetime

from django.db import IntegrityError
from django.db.models import Avg
from rest_framework import serializers

from src.market.models import ShopUnit


class ShopUnitImportSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    date = serializers.CharField(max_length=100)
    parentId = serializers.UUIDField(allow_null=True)

    class Meta:
        model = ShopUnit
        fields = ('id', 'name', 'date', 'parentId', 'type', 'price')

    def create(self, validated_data):
        validated_data['parentId'] = ShopUnit.objects.get_unit_or_none(id=validated_data.get('parentId'))
        shop_unit = ShopUnit.objects.get_unit_or_none(id=validated_data.get('id'))

        if shop_unit is not None:
            if shop_unit.type != validated_data['type']:
                raise serializers.ValidationError()
            shop_unit.name = validated_data['name']
            shop_unit.parentId = validated_data['parentId']
            shop_unit.price = validated_data['price']
            shop_unit.date = validated_data['date']
            shop_unit.save()
        else:
            try:
                shop_unit = ShopUnit.objects.create(**validated_data)
            except IntegrityError:
                raise serializers.ValidationError()
        return shop_unit

    def validate(self, value):
        self._validate_parentId(value['parentId'])
        self._validate_price(value['price'], value["type"])
        self._validate_date(value['date'])
        self._validate_name(value['name'], value["id"])
        return value

    def _validate_parentId(self, value):
        unit = ShopUnit.objects.get_unit_or_none(id=value)
        if unit:
            if unit.type == 'OFFER':
                print("failed _validate_parentId")
                raise serializers.ValidationError()
        else:
            if value is not None:
                print("failed _validate_parentId")
                raise serializers.ValidationError()

    def _validate_price(self, value, type):
        if type == 'OFFER':
            if value is None:
                print(" failed _validate_price")
                raise serializers.ValidationError()
            elif value < 0:
                print(" failed _validate_price")
                raise serializers.ValidationError()
        if type == 'CATEGORY' and value is not None:
            print(" failed _validate_price")
            raise serializers.ValidationError()

    def _validate_date(self, value):
        try:
            datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            print("failed _validate_date")
            raise serializers.ValidationError()

    def _validate_name(self, value, id):
        if ShopUnit.objects.get_unit_or_none(id=id):
            return value
        else:
            if ShopUnit.objects.get_unit_or_none(name=value):
                print("failed _validate_name")
                raise serializers.ValidationError()


class ShopUnitDetailSerializer(serializers.ModelSerializer):
    average_price = serializers.SerializerMethodField('average_price_category')

    def average_price_category(self, shop_unit):
        return shop_unit.children.all().aggregate(Avg('price'))

    class Meta:
        model = ShopUnit
        fields = ('id', 'name', 'date', 'type', 'price', 'parentId', 'children', 'average_price')
        depth = 1
