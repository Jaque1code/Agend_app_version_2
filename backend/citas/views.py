from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Cita, BloqueoAgenda
from .serializers import CitaReadSerializer, CitaCreateSerializer, BloqueoAgendaSerializer
from profesionales.models import Profesional, HorarioDisponible
from catalogos.models import Servicio


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all().order_by('-fecha_hora_inicio')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CitaCreateSerializer
        return CitaReadSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        cliente_id = self.request.query_params.get('cliente')
        profesional_id = self.request.query_params.get('profesional')
        estado = self.request.query_params.get('estado')

        if cliente_id:
            queryset = queryset.filter(id_cliente_id=cliente_id)
        if profesional_id:
            queryset = queryset.filter(id_profesional_id=profesional_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset


class BloqueoAgendaViewSet(viewsets.ModelViewSet):
    queryset = BloqueoAgenda.objects.all()
    serializer_class = BloqueoAgendaSerializer
    permission_classes = [AllowAny]


class DisponibilidadView(APIView):
    """
    Cálculo de slots disponibles:
    GET /api/citas/disponibilidad/?profesional=1&servicio=1&fecha=2026-08-31
    """
    permission_classes = [AllowAny]

    def get(self, request):
        profesional_id = request.query_params.get('profesional')
        servicio_id = request.query_params.get('servicio')
        fecha_str = request.query_params.get('fecha')

        if not (profesional_id and servicio_id and fecha_str):
            return Response(
                {"error": "Debe proporcionar profesional, servicio y fecha (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha_consulta = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Obtener Servicio y su duración
        try:
            servicio = Servicio.objects.get(id_servicio=servicio_id, activo=True)
        except Servicio.DoesNotExist:
            return Response({"error": "Servicio no encontrado o inactivo."}, status=status.HTTP_404_NOT_FOUND)

        duracion_min = servicio.duracion_minutos

        # 2. Obtener día de la semana (0=Domingo, 1=Lunes, ..., 6=Sábado en PostgreSQL)
        # Python weekday(): 0=Lunes, 6=Domingo -> Conversión:
        dia_postgres = (fecha_consulta.weekday() + 1) % 7

        # 3. Consultar horario laboral del profesional para ese día
        horarios = HorarioDisponible.objects.filter(id_profesional_id=profesional_id, dia_semana=dia_postgres)
        if not horarios.exists():
            return Response({"fecha": fecha_str, "slots_disponibles": [], "mensaje": "El profesional no atiende este día."})

        # 4. Obtener citas activas y bloqueos de ese día
        tz = timezone.get_current_timezone()
        inicio_dia = timezone.make_aware(datetime.combine(fecha_consulta, datetime.min.time()), tz)
        fin_dia = timezone.make_aware(datetime.combine(fecha_consulta, datetime.max.time()), tz)

        citas_ocupadas = Cita.objects.filter(
            id_profesional_id=profesional_id,
            fecha_hora_inicio__gte=inicio_dia,
            fecha_hora_fin__lte=fin_dia
        ).exclude(estado='CANCELADA')

        bloqueos = BloqueoAgenda.objects.filter(
            id_profesional_id=profesional_id,
            fecha_inicio__lt=fin_dia,
            fecha_fin__gt=inicio_dia
        )

        slots_disponibles = []

        # 5. Generar y evaluar bloques
        for h in horarios:
            cursor = timezone.make_aware(datetime.combine(fecha_consulta, h.hora_inicio), tz)
            limite = timezone.make_aware(datetime.combine(fecha_consulta, h.hora_fin), tz)

            while cursor + timedelta(minutes=duracion_min) <= limite:
                slot_fin = cursor + timedelta(minutes=duracion_min)

                # Verificar si solapa con alguna cita existente
                choca_cita = any(
                    (cursor < c.fecha_hora_fin and slot_fin > c.fecha_hora_inicio)
                    for c in citas_ocupadas
                )

                # Verificar si solapa con algún bloqueo
                choca_bloqueo = any(
                    (cursor < b.fecha_fin and slot_fin > b.fecha_inicio)
                    for b in bloqueos
                )

                if not choca_cita and not choca_bloqueo:
                    slots_disponibles.append({
                        "hora_inicio": cursor.strftime("%H:%M"),
                        "hora_fin": slot_fin.strftime("%H:%M"),
                        "datetime_inicio": cursor.isoformat(),
                        "datetime_fin": slot_fin.isoformat()
                    })

                # Siguiente slot cada 30 min (o paso configurable)
                cursor += timedelta(minutes=30)

        return Response({
            "profesional_id": profesional_id,
            "servicio": servicio.nombre,
            "duracion_min": duracion_min,
            "fecha": fecha_str,
            "total_slots": len(slots_disponibles),
            "slots": slots_disponibles
        })
