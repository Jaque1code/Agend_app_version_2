from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Profesional, HorarioDisponible, ProfesionalServicio
from .serializers import (
    ProfesionalSerializer,
    HorarioDisponibleSerializer,
    AsignarServiciosSerializer
)
from catalogos.models import Servicio

class ProfesionalViewSet(viewsets.ModelViewSet):
    # Traer todos los profesionales sin filtrar por texto rígido de estado laboral
    queryset = Profesional.objects.all()
    serializer_class = ProfesionalSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        sucursal_id = self.request.query_params.get('sucursal')
        servicio_id = self.request.query_params.get('servicio')

        if sucursal_id:
            queryset = queryset.filter(id_sucursal_id=sucursal_id)
        if servicio_id:
            try:
                # Filtrar mediante la tabla intermedia ProfesionalServicio
                profesionales_ids = ProfesionalServicio.objects.filter(
                    id_servicio_id=servicio_id
                ).values_list('id_profesional_id', flat=True)
                queryset = queryset.filter(id_profesional__in=profesionales_ids)
            except Exception:
                pass
        return queryset.distinct()

    # Endpoint personalizado: POST /api/personal/profesionales/{id}/asignar_servicios/
    @action(detail=True, methods=['post'], serializer_class=AsignarServiciosSerializer)
    def asignar_servicios(self, request, pk=None):
        profesional = self.get_object()
        serializer = AsignarServiciosSerializer(data=request.data)

        if serializer.is_valid():
            servicios_ids = serializer.validated_data['servicios_ids']
            
            # Limpiar y registrar en tabla intermedia ProfesionalServicio
            ProfesionalServicio.objects.filter(id_profesional=profesional).delete()
            for s_id in servicios_ids:
                servicio_obj = Servicio.objects.filter(id_servicio=s_id).first()
                if servicio_obj:
                    ProfesionalServicio.objects.create(
                        id_profesional=profesional,
                        id_servicio=servicio_obj
                    )

            return Response(
                {"mensaje": "Servicios asignados correctamente al profesional.", "servicios_ids": servicios_ids},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HorarioDisponibleViewSet(viewsets.ModelViewSet):
    queryset = HorarioDisponible.objects.all().order_by('dia_semana', 'hora_inicio')
    serializer_class = HorarioDisponibleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        profesional_id = self.request.query_params.get('profesional')
        if profesional_id:
            queryset = queryset.filter(id_profesional_id=profesional_id)
        return queryset