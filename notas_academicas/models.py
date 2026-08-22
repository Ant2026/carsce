from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from inicio_sesion.models import MateriaAsignada, PeriodoCargarNotas, Docente, Usuario, PeriodoNotasMateria, Estudiante, Materia, DocenteAsignadoMateria, Pnf, Nucleos

class PlanActividadAcademica(models.Model):
    id_plan = models.AutoField(primary_key=True)
    pnf = models.ForeignKey(Pnf, models.PROTECT)
    nucleo = models.ForeignKey(Nucleos, models.PROTECT)
    materia_asignacion = models.ForeignKey(MateriaAsignada, on_delete=models.PROTECT)
    periodo_academico = models.ForeignKey(PeriodoCargarNotas, on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    observacion = models.TextField(blank=True, null=True)

    ESTADOS_ACEPTACION = [
        ("BORRADOR", "Borrador"),
        ("ENVIADO", "Enviado al Coordinador"),
        ("ACEPTADA", "Aceptada"),
        ("DENEGADA", "Denegada"),
    ]

    estado_aceptacion = models.CharField(max_length=10, choices=ESTADOS_ACEPTACION, default="BORRADOR")

class DetallePlanActividades(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    plan_academico = models.ForeignKey(PlanActividadAcademica, on_delete=models.CASCADE, related_name="detalles")
    titulo_unidad = models.CharField(max_length=255)
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2)
    contenido_unidad = models.TextField()

class DetallePlanEvaluacion(models.Model):
    id_evaluacion = models.AutoField(primary_key=True)
    detalle_plan = models.ForeignKey(DetallePlanActividades, on_delete=models.CASCADE, related_name="evaluaciones")
    metodo_evaluacion = models.CharField(max_length=100)
    porcentaje_evaluacion = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_evaluacion = models.DateField()

# Notas académicas

class PromedioFinal(models.Model):
    id_promedio_final = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name="promedios_finales")
    materia_asignacion = models.ForeignKey(MateriaAsignada, on_delete=models.PROTECT, related_name="promedios_finales")
    trayecto = models.CharField(max_length=20)
    promedio_final = models.DecimalField(max_digits=5, decimal_places=2)
    estado = models.CharField(max_length=100)
    fecha_promedio = models.DateField()

class Reparacion(models.Model):
    id_reparacion = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, models.PROTECT, related_name="reparaciones")
    materia_asignacion = models.ForeignKey(MateriaAsignada, models.PROTECT, related_name="reparaciones")
    calificacion = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_reparacion = models.DateField()
    trayecto = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=100)

class Calificaciones(models.Model):
    id_calificaciones = models.AutoField(primary_key=True)
    periodo_materia = models.ForeignKey(PeriodoNotasMateria, on_delete=models.PROTECT, related_name="calificaciones")
    materia_asignada = models.ForeignKey(MateriaAsignada, on_delete=models.PROTECT, related_name="calificaciones", blank=True, null=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name="calificaciones")
    promedio_tramo = models.DecimalField(max_digits=5, decimal_places=2)
    asistencia = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        default=0
    )
    condicion = models.CharField(max_length=100)
    trayecto = models.CharField(max_length=20)
    fecha_promedio = models.DateField()

class DetalleCalificacionesUnidad(models.Model):
    id_detalle_calificaciones_unidad = models.AutoField(primary_key=True)
    calificacion = models.ForeignKey(Calificaciones, on_delete=models.PROTECT, related_name="detalles_unidad")
    unidad = models.ForeignKey(DetallePlanActividades, on_delete=models.PROTECT, related_name="calificaciones_unidad")
    nota_unidad = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_calificacion = models.DateField(auto_now_add=True)

class DetalleCalificaciones(models.Model):
    id_detalle_calificaciones = models.AutoField(primary_key=True)
    calificacion = models.ForeignKey(Calificaciones, on_delete=models.PROTECT, related_name="detalles_evaluacion")
    evaluacion = models.ForeignKey(DetallePlanEvaluacion, on_delete=models.PROTECT, related_name="calificaciones")
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_calificacion = models.DateField(auto_now_add=True)

# Respaldo de notas académicas

class HistorialModificacionNotas(models.Model):
    id_historial = models.AutoField(primary_key=True)
    docente_asignado = models.ForeignKey(DocenteAsignadoMateria, on_delete=models.PROTECT)
    periodo_academico = models.ForeignKey(PeriodoCargarNotas, on_delete=models.PROTECT)
    trayecto = models.CharField(max_length=50)
    fecha_modificacion = models.DateTimeField(auto_now_add=True)
    usuario_modifica = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    motivo = models.TextField()

    def __str__(self):
        return f"Modificación {self.id_historial}"

class HistorialDetalleNota(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    historial = models.ForeignKey(HistorialModificacionNotas, on_delete=models.CASCADE, related_name="detalles")
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT)
    numero_unidad = models.PositiveSmallIntegerField()
    nota_anterior = models.DecimalField(max_digits=5, decimal_places=2)
    nota_nueva = models.DecimalField(max_digits=5, decimal_places=2)
    asistencia_anterior = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    asistencia_nueva = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    promedio_anterior = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    promedio_nuevo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

# Promedio Final y Actualización de Trayecto

class HistorialTrayectoEstudiante(models.Model):

    id_historial = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name="historiales_trayecto")
    anio = models.PositiveIntegerField()
    trayecto_anterior = models.CharField(max_length=20)
    trayecto_nuevo = models.CharField(max_length=20)
    cantidad_materias = models.PositiveSmallIntegerField()
    materias_reprobadas = models.PositiveSmallIntegerField()
    materias_mala_asistencia = models.PositiveSmallIntegerField()
    estado = models.CharField(max_length=50)
    puede_pasar = models.BooleanField(default=False)
    motivo = models.TextField()
    fecha_procesamiento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.estudiante} - "
            f"{self.anio} - "
            f"{self.trayecto_anterior}"
        )

