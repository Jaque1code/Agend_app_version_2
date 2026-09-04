from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfesionalViewSet, HorarioDisponibleViewSet

router = DefaultRouter()
router.register(r'profesionales', ProfesionalViewSet, basename='profesional')
router.register(r'horarios', HorarioDisponibleViewSet, basename='horario')

urlpatterns = [
    path('', include(router.urls)),
]







