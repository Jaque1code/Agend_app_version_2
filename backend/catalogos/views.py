from rest_framework import viewsets, permissions
from .models import Sucursal, Servicio
from .serializers import SucursalSerializer, ServicioSerializer

class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.filter(activo=True)
    serializer_class = SucursalSerializer
    permission_classes = [permissions.AllowAny]


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.filter(activo=True)
    serializer_class = ServicioSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        sucursal_id = self.request.query_params.get('sucursal')
        if sucursal_id:
            queryset = queryset.filter(id_sucursal_id=sucursal_id)
        return queryset

