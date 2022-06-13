from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError as RestValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.market.models import ShopUnit
from src.market.serializers import ShopUnitImportSerializer, ShopUnitDetailSerializer
from src.services.response_status_codes import custom_response


class ShopUnitImportView(CreateAPIView):
    serializer_class = ShopUnitImportSerializer
    queryset = ShopUnit.objects.all()

    def create(self, request, *args, **kwargs):
        updateDate = request.data.get('updateDate')

        if not updateDate:
            return custom_response(status_code=HTTP_400_BAD_REQUEST,
                                   message="ValidationError : update date was not sent")

        items = request.data.get('items', [])

        if not items:
            return custom_response(status_code=HTTP_400_BAD_REQUEST, message="ValidationError : Items list is empty")

        for item in items:
            item.update({'date': updateDate})

        serializer = self.get_serializer(data=items, many=True)
        try:
            serializer.is_valid(raise_exception=True)
        except RestValidationError as e:
            print(e)
            return custom_response(status_code=HTTP_400_BAD_REQUEST, message="Validation Error")

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class ShopUnitDetailView(RetrieveAPIView):
    serializer_class = ShopUnitDetailSerializer
    queryset = ShopUnit.objects.all()


@api_view(http_method_names=['DELETE'])
def delete_shop_unit(request, *args, **kwargs):
    try:
        unit = ShopUnit.objects.get(id=kwargs.get("id"))
    except DjangoValidationError:
        return custom_response(status_code=HTTP_400_BAD_REQUEST, message=f"Validation Error: Is not a valid UUID")
    except ShopUnit.DoesNotExist:
        return custom_response(status_code=HTTP_404_NOT_FOUND, message="Item not found")
    unit.delete()  # CASCADE

    return Response(200)
