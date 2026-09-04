from django.db import models
from authentication.models import Usuario
from catalogos.models import Sucursal, Servicio

class Profesional(models.Model):
    id_profesional = models.BigAutoField(primary_key=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_sucursal= models.ForeignKey(Sucursal, on_delete=models.CASCADE, db_column='id_sucursal')
    especialidad = models.CharField(max_length=100, null=True, blank=True)
    porcentaje_comision = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    estado_laboral = models.CharField(max_length=20, default='ACTIVO')
     


    servicios = models.ManyToManyField(
        Servicio,
        through='ProfesionalServicio',
        related_name='profesionales'
    )

    class Meta:
        db_table = 'profesional'
        managed = False

    @property
    def id(self):
        return self.id_profesional

    def __str__(self):
        return f"{self.id_usuario.nombre} {self.id_usuario.apellido} - {self.especialidad or 'Especialista'}"


class ProfesionalServicio(models.Model):
    id_profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        db_column='id_profesional'
    )
    id_servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        db_column='id_servicio'
    )

    class Meta:
        db_table = 'profesional_servicio'
        managed = False
        unique_together = (('id_profesional', 'id_servicio'),)



class HorarioDisponible(models.Model):
    id_horario = models.BigAutoField(primary_key=True)
    id_profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        db_column='id_profesional',
        related_name='horarios'
    )
    dia_semana = models.SmallIntegerField()  # 0=Domingo, 1=Lunes, ..., 6=Sábado
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        db_table = 'horario_disponible'
        managed = False

    @property
    def id(self):
        return self.id_horario

    def __str__(self):
        dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        dia_str = dias[self.dia_semana] if 0 <= self.dia_semana <= 6 else str(self.dia_semana)
        return f"{dia_str}: {self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"
