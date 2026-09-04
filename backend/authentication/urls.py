from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegistroClienteView, LoginView

urlpatterns = [
    path('register/', RegistroClienteView.as_view(), name='registro_cliente'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]