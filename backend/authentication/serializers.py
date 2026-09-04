from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'apellido', 'correo', 'telefono', 'password']

    def create(self, validated_data):
        return Usuario.objects.create_user(
            correo=validated_data['correo'],
            nombre=validated_data['nombre'],
            apellido=validated_data['apellido'],
            telefono=validated_data.get('telefono', ''),
            password=validated_data['password'],
            id_rol=4
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['nombre'] = f"{user.nombre} {user.apellido}"
        token['correo'] = user.correo
        token['rol'] = user.id_rol.nombre
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['usuario'] = {
            'id': self.user.id_usuario,
            'nombre': self.user.nombre,
            'apellido': self.user.apellido,
            'correo': self.user.correo,
            'rol': self.user.id_rol.nombre
        }
        return data