from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SucursalViewSet, ServicioViewSet

router = DefaultRouter()
router.register(r'sucursales', SucursalViewSet, basename='sucursal')
router.register(r'servicios', ServicioViewSet, basename='servicio')

urlpatterns = [
    path('', include(router.urls)),
]













