from rest_framework import serializers
from .models import Sucursal, Servicio

class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ['id_sucursal', 'nombre', 'rut_empresa', 'telefono', 'direccion', 'correo', 'activo', 'fecha_creacion']


class ServicioSerializer(serializers.ModelSerializer):
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal.nombre')

    class Meta:
        model = Servicio
        fields = [
            'id_servicio',
            'id_sucursal',
            'nombre_sucursal',
            'nombre',
            'descripcion',
            'duracion_minutos',
            'precio',
            'activo'
        ]





