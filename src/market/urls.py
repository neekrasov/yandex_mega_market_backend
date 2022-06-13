from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from src.market import views
from src.market.views import delete_shop_unit, ShopUnitDetailView

schema_view = get_schema_view(
    openapi.Info(
        title="Yandex Market",
        default_version='v0.0.1',
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('imports/', views.ShopUnitImportView.as_view()),
    path('delete/<str:id>', delete_shop_unit),
    path('nodes/<str:pk>', ShopUnitDetailView.as_view()),
]
