from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Rol(models.Model):
    id_rol = models.SmallAutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        db_table = 'roles'
        managed = False

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def get_by_natural_key(self, correo):
        return self.get(correo=correo)

    def create_user(self, correo, nombre, apellido, password=None, id_rol=4, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        rol = Rol.objects.get(id_rol=id_rol)
        user = self.model(correo=correo, nombre=nombre, apellido=apellido, id_rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    id_usuario = models.BigAutoField(primary_key=True)
    id_rol = models.ForeignKey(Rol, on_delete=models.DO_NOTHING, db_column='id_rol')
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.EmailField(max_length=150, unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    password = models.CharField(max_length=255, db_column='clave_hash')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        db_table = 'usuario'
        managed = False

    @property
    def id(self):
        return self.id_usuario

    @property
    def is_active(self):
        return self.activo

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True