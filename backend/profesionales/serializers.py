from rest_framework import serializers
from .models import Profesional, HorarioDisponible

class HorarioDisponibleSerializer(serializers.ModelSerializer):
    nombre_dia = serializers.SerializerMethodField()

    class Meta:
        model = HorarioDisponible
        fields = ['id_horario', 'dia_semana', 'nombre_dia', 'hora_inicio', 'hora_fin']

    def get_nombre_dia(self, obj):
        dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        if hasattr(obj, 'dia_semana') and 0 <= obj.dia_semana <= 6:
            return dias[obj.dia_semana]
        return 'Desconocido'


class ProfesionalSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    correo = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    nombre_sucursal = serializers.SerializerMethodField()
    horarios = HorarioDisponibleSerializer(many=True, read_only=True)

    class Meta:
        model = Profesional
        fields = [
            'id_profesional',
            'id_usuario',
            'id_sucursal',
            'nombre_completo',
            'correo',
            'telefono',
            'nombre_sucursal',
            'especialidad',
            'porcentaje_comision',
            'estado_laboral',
            'horarios'
        ]

    def get_nombre_completo(self, obj):
        try:
            return f"{obj.id_usuario.nombre} {obj.id_usuario.apellido}".strip()
        except Exception:
            return f"Profesional #{obj.id_profesional}"

    def get_correo(self, obj):
        try:
            return obj.id_usuario.correo or ""
        except Exception:
            return ""

    def get_telefono(self, obj):
        try:
            return obj.id_usuario.telefono or ""
        except Exception:
            return ""

    def get_nombre_sucursal(self, obj):
        try:
            if hasattr(obj, 'id_sucursal') and obj.id_sucursal:
                return getattr(obj.id_sucursal, 'nombre_comercial', getattr(obj.id_sucursal, 'nombre', 'Principal'))
        except Exception:
            pass
        return "Principal"


class AsignarServiciosSerializer(serializers.Serializer):
    servicios_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )