from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.market.models import ShopUnit
from src.market.serializers import ShopUnitImportSerializer, ShopUnitDetailSerializer, \
    ShopUnitSerializer
from src.services import exceptions
from src.services.exceptions import ValidationError
from src.services.response_status_codes import custom_response
from src.services.services import price_calculation
from src.services.validators import validate_date


class ShopUnitImportView(CreateAPIView):
    serializer_class = ShopUnitImportSerializer
    queryset = ShopUnit.objects.all()

    def create(self, request, *args, **kwargs):
        updateDate = request.data.get('updateDate')

        # Валидация на наличие обязательного поля updateDate.
        if not updateDate:
            return custom_response(status_code=HTTP_400_BAD_REQUEST,
                                   message="ValidationError : Update date was not sent")

        items = request.data.get('items', [])

        # Валидация пустого списка items, дублирования id и name.
        if not items:
            return custom_response(status_code=HTTP_400_BAD_REQUEST, message="ValidationError : Items list is empty")
        else:
            duplicates = dict()
            for item in items:
                duplicates[item['id']] = duplicates.get(item['id'], 0) + 1
                if duplicates[item['id']] > 1:
                    return custom_response(status_code=HTTP_400_BAD_REQUEST,
                                           message="ValidationError: Dubplicate 'id' field")
                duplicates[item['name']] = duplicates.get(item['name'], 0) + 1
                if duplicates[item['name']] > 1:
                    return custom_response(status_code=HTTP_400_BAD_REQUEST,
                                           message="ValidationError: Dubplicate 'name' field")
                # Обновление даты для каждого юнита.
                item.update({'date': updateDate})

        # Передача данных в сериализатор - валидация.
        serializer = self.get_serializer(data=items, many=True)
        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.ValidationError as e:
            return custom_response(status_code=HTTP_400_BAD_REQUEST, message=f"Validation Error: {e}")

        # Сохранение данных
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Перерасчёт поля price у категорий.
        changed_categories = set(
            ShopUnit.objects.get_unit_or_none(
                id=unit["parentId"]) for unit in items if unit["parentId"] is not None)
        for category_id in changed_categories:
            price_calculation(category_id)

        return Response(status=status.HTTP_200_OK, headers=headers)


class ShopUnitDetailView(RetrieveAPIView):
    serializer_class = ShopUnitDetailSerializer
    queryset = ShopUnit.objects.all()


class ShopUnitSalesView(ListAPIView):
    serializer_class = ShopUnitSerializer

    def get_queryset(self):
        query = self.request.GET.get('date')
        if query is None:
            raise ValidationError("query parameter 'date' must be sent")
        date = validate_date(query)
        return ShopUnit.objects.filter(date__gte=date - timedelta(hours=24), date__lte=date,  type="OFFER")

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except ValidationError as e:
            return custom_response(HTTP_400_BAD_REQUEST, message=f"Validation Error: {e}")


@api_view(http_method_names=['DELETE'])
def delete_shop_unit(request, *args, **kwargs):
    try:
        unit = ShopUnit.objects.get(id=kwargs.get("id"))
    except DjangoValidationError:
        return custom_response(status_code=HTTP_400_BAD_REQUEST, message=f"Validation Error: Is not a valid UUID")
    except ShopUnit.DoesNotExist:
        return custom_response(status_code=HTTP_404_NOT_FOUND, message="Item not found")
    unit.delete()  # CASCADE

    price_calculation(unit.parentId)
    return Response(200)
