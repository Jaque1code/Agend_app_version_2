from django.db import models

class Sucursal(models.Model):
    id_sucursal = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, db_column='nombre_comercial')
    rut_empresa = models.CharField(max_length=12, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    correo = models.CharField(max_length=150, null=True, blank=True)
    activo = models.BooleanField(default=True, db_column='estado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sucursal'
        managed = False

    @property
    def id(self):
        return self.id_sucursal

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    id_servicio = models.BigAutoField(primary_key=True)
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, db_column='id_sucursal')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2, db_column='precio_base')
    duracion_minutos = models.IntegerField(db_column='duracion_min')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'servicio'
        managed = False

    @property
    def id(self):
        return self.id_servicio

    def __str__(self):
        return f"{self.nombre} (${self.precio})"