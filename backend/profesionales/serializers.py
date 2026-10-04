from rest_framework import serializers
from django.db import transaction
from authentication.models import Usuario
from .models import Profesional, HorarioDisponible

class HorarioDisponibleSerializer(serializers.ModelSerializer):
    nombre_dia = serializers.SerializerMethodField(read_only=True)
    id_profesional = serializers.PrimaryKeyRelatedField(
        queryset=Profesional.objects.all(),
        required=True
    )

    class Meta:
        model = HorarioDisponible
        fields = [
            'id_horario',
            'id_profesional',
            'dia_semana',
            'nombre_dia',
            'hora_inicio',
            'hora_fin'
        ]

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

    # Campos de solo escritura para el formulario de alta
    nombre = serializers.CharField(write_only=True, required=False)
    apellido = serializers.CharField(write_only=True, required=False)
    correo_nuevo = serializers.EmailField(write_only=True, required=False)
    telefono_nuevo = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Profesional
        fields = [
            'id_profesional',
            'id_usuario',
            'nombre_completo',
            'correo',
            'telefono',
            'nombre_sucursal',
            'especialidad',
            'porcentaje_comision',
            'estado_laboral',
            'horarios',
            'nombre',
            'apellido',
            'correo_nuevo',
            'telefono_nuevo',
            'password',
        ]
        # Si el modelo Profesional tiene id_sucursal o id_local en BD, los dejamos flexibles:
        extra_kwargs = {
            'id_usuario': {'required': False, 'allow_null': True}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adaptación dinámica al nombre del campo de sucursal en el modelo (id_sucursal o id_local)
        for campo_fk in ['id_sucursal', 'id_local']:
            if hasattr(self.Meta.model, campo_fk):
                if campo_fk not in self.fields:
                    self.fields[campo_fk] = serializers.PrimaryKeyRelatedField(
                        queryset=self.Meta.model._meta.get_field(campo_fk).related_model.objects.all(),
                        required=False,
                        allow_null=True
                    )

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
            sucursal = getattr(obj, 'id_sucursal', getattr(obj, 'id_local', None))
            if sucursal:
                return getattr(sucursal, 'nombre_comercial', getattr(sucursal, 'nombre', 'Principal'))
        except Exception:
            pass
        return "Principal"

    def create(self, validated_data):
        nombre = validated_data.pop('nombre', '')
        apellido = validated_data.pop('apellido', '')
        correo = validated_data.pop('correo_nuevo', '')
        telefono = validated_data.pop('telefono_nuevo', '')
        raw_password = validated_data.pop('password', 'Clave123.')

        with transaction.atomic():
            usuario = validated_data.get('id_usuario', None)
            if not usuario and correo:
                # Validar si el correo ya existe para evitar la excepción IntegrityError
                usuario_existente = Usuario.objects.filter(correo=correo).first()
                if usuario_existente:
                    usuario = usuario_existente
                else:
                    usuario = Usuario.objects.create(
                        nombre=nombre,
                        apellido=apellido,
                        correo=correo,
                        telefono=telefono,
                        id_rol_id=2,  # PROFESIONAL
                        activo=True
                    )
                    usuario.set_password(raw_password)
                    usuario.save()

                validated_data['id_usuario'] = usuario

            return super().create(validated_data)


class AsignarServiciosSerializer(serializers.Serializer):
    servicios_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )