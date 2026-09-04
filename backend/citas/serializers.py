from rest_framework import serializers
from .models import Cita, BloqueoAgenda

class CitaReadSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    profesional_nombre = serializers.SerializerMethodField()
    servicio_nombre = serializers.ReadOnlyField(source='id_servicio.nombre')
    sucursal_nombre = serializers.ReadOnlyField(source='id_sucursal.nombre')
    precio = serializers.ReadOnlyField(source='id_servicio.precio')

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
        return f"{obj.id_cliente.nombre} {obj.id_cliente.apellido}".strip()

    def get_profesional_nombre(self, obj):
        return f"{obj.id_profesional.id_usuario.nombre} {obj.id_profesional.id_usuario.apellido}".strip()


class CitaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = [
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
            'estado': {'default': 'PENDIENTE'}
        }


class BloqueoAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloqueoAgenda
        fields = '__all__'



