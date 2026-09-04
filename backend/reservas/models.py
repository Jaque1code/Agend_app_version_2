from django.db import models
from authentication.models import Usuario
from catalogos.models import Sucursal, Servicio
from profesionales.models import Profesional

class Cita(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('COMPLETADA', 'Completada'),
    ]

    id_cita = models.BigAutoField(primary_key=True)
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, db_column='id_sucursal')
    id_cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_cliente')
    id_profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, db_column='id_profesional')
    id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, db_column='id_servicio')
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    estado = models.CharField(max_length=25, choices=ESTADOS, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cita'
        managed = False
        app_label = 'reservas'

    @property
    def id(self):
        return self.id_cita

    def __str__(self):
        return f"Cita #{self.id_cita} - {self.id_cliente.nombre} con {self.id_profesional} ({self.estado})"


class BloqueoAgenda(models.Model):
    id_bloqueo = models.BigAutoField(primary_key=True)
    id_profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, db_column='id_profesional')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    motivo = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'bloqueos_agenda'
        managed = False
        app_label = 'reservas'

    @property
    def id(self):
        return self.id_bloqueo

    def __str__(self):
        return f"Bloqueo #{self.id_bloqueo} - {self.id_profesional} ({self.motivo})"


