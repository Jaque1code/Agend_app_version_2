from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet, BloqueoAgendaViewSet, DisponibilidadView

router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='cita')
router.register(r'bloqueos', BloqueoAgendaViewSet, basename='bloqueo')

urlpatterns = [
    path('disponibilidad/', DisponibilidadView.as_view(), name='disponibilidad'),
    path('', include(router.urls)),
]













