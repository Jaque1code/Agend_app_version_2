from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Cita, BloqueoAgenda
from catalogos.models import Servicio
from profesionales.models import HorarioDisponible

class CitaReadSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    profesional_nombre = serializers.SerializerMethodField()
    servicio_nombre = serializers.ReadOnlyField(source='id_servicio.nombre')
    sucursal_nombre = serializers.ReadOnlyField(source='id_sucursal.nombre_comercial')
    precio = serializers.ReadOnlyField(source='id_servicio.precio_base')

    class Meta:
        model = Cita
        fields = [
            'id_cita',
            'id_sucursal',
            'sucursal_nombre',
            'id_cliente',
            'cliente_nombre',
            'id_profesional',
            'profesional_nombre',
            'id_servicio',
            'servicio_nombre',
            'precio',
            'fecha_hora_inicio',
            'fecha_hora_fin',
            'estado',
            'fecha_creacion'
        ]

    def get_cliente_nombre(self, obj):
        if not obj.id_cliente:
            return "Sin cliente"
        return f"{obj.id_cliente.nombre} {obj.id_cliente.apellido}".strip()

    def get_profesional_nombre(self, obj):
        if not obj.id_profesional or not hasattr(obj.id_profesional, 'id_usuario'):
            return "Sin profesional"
        return f"{obj.id_profesional.id_usuario.nombre} {obj.id_profesional.id_usuario.apellido}".strip()


class CitaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = [
            'id_cita',
            'id_sucursal',
            'id_cliente',
            'id_profesional',
            'id_servicio',
            'fecha_hora_inicio',
            'fecha_hora_fin',
            'estado'
        ]
        extra_kwargs = {
            'fecha_hora_fin': {'required': False},
            'estado': {'default': 'CONFIRMADA'}
        }

    def validate(self, attrs):
        profesional = attrs.get('id_profesional')
        servicio = attrs.get('id_servicio')
        inicio = attrs.get('fecha_hora_inicio')

        if not inicio:
            raise serializers.ValidationError({"fecha_hora_inicio": "Debe especificar la fecha y hora de inicio."})

        # 1. Calcular automáticamente la hora de fin según la duración del servicio
        duracion = getattr(servicio, 'duracion_minutos', getattr(servicio, 'duracion_min', 30))
        fin = inicio + timedelta(minutes=duracion)
        attrs['fecha_hora_fin'] = fin

        # 2. Validar que no sea un DÍA anterior a hoy (evita el bloqueo por diferencia horaria UTC/Chile)
        ahora_local = timezone.localtime(timezone.now()).date()
        fecha_reserva = inicio.date() if hasattr(inicio, 'date') else inicio

        if fecha_reserva < ahora_local:
            raise serializers.ValidationError({
                "fecha_hora_inicio": "No se pueden agendar citas en fechas anteriores a hoy."
            })

        # 3. Validar solapamiento con otras citas activas del profesional
        citas_solapadas = Cita.objects.filter(
            id_profesional=profesional,
            fecha_hora_inicio__lt=fin,
            fecha_hora_fin__gt=inicio
        ).exclude(estado='CANCELADA')

        if self.instance:
            citas_solapadas = citas_solapadas.exclude(id_cita=self.instance.id_cita)

        if citas_solapadas.exists():
            raise serializers.ValidationError({
                "solapamiento": "El profesional ya tiene una cita reservada en este intervalo de tiempo."
            })

        # 4. Validar colisión con bloqueos de agenda
        bloqueos = BloqueoAgenda.objects.filter(
            id_profesional=profesional,
            fecha_inicio__lt=fin,
            fecha_fin__gt=inicio
        )
        if bloqueos.exists():
            raise serializers.ValidationError({
                "bloqueo": "El horario seleccionado coincide con un bloqueo de agenda del profesional."
            })

        return attrs


class BloqueoAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloqueoAgenda
        fields = '__all__'