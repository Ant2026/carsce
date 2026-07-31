from django.db import models
from django.contrib.contenttypes.models import ContentType

# Clases (Tablas) principales 

# ESTATICO
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    genero = models.CharField(max_length=50)
    cedula_identidad = models.CharField(max_length=15)
    estado_civil = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

# ESTATICO
class Cuenta(models.Model):
    id_cuenta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    usuario = models.CharField(max_length=160, unique=True)
    clave = models.CharField(max_length=160)
    tipo_cuenta = models.CharField(
        max_length=20,
        choices=[
            ("ADMIN", "Administrativo"),
            ("EST", "Estudiante"),
        ]
    )

# ESTATICO
class Residencia(models.Model):
    id_residencia = models.AutoField(primary_key=True)
    condicion_residencia = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    parroquia = models.CharField(max_length=100)
    direccion_residencia = models.CharField(max_length=100)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='residencia')

# ESTATICO
class Contacto(models.Model):
    id_contacto = models.AutoField(primary_key=True)
    telefono_suplete = models.CharField(max_length=15, null=True, blank=True)
    telefono_personal = models.CharField(max_length=15)
    correo_electronico = models.EmailField(max_length=100, unique=True)
    correo_alternativo = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='contacto')

# ESTATICO
class Nacimiento(models.Model):
    id_nacimiento = models.AutoField(primary_key=True)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    parroquia = models.CharField(max_length=100)
    direccion_nacimiento = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='nacimiento')

# ESTATICO
class Pnf(models.Model):
    id_pnf = models.AutoField(primary_key=True)
    pnf = models.CharField(max_length=50)
    codigo = models.CharField(max_length=40)
    periodo_academico = models.CharField(max_length=40, null=True, blank=True)
    
    def __str__(self):
        return self.pnf

# ESTATICO
class Nucleos(models.Model):
    id_nucleo = models.AutoField(primary_key=True)
    municipio = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)

    def __str__(self):
        return self.municipio

# ESTATICO
class PNFNucleo(models.Model):
    id_pnf_nucleo = models.AutoField(primary_key=True)
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE, db_column='id_nucleo')
    id_pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE, db_column='id_pnf')

    def __str__(self):
        return f"{self.id_pnf.pnf} - {self.id_nucleo.municipio}"

# ESTATICO
class AulaAcademica(models.Model):
    id_aula = models.AutoField(primary_key=True)
    nombre_aula = models.CharField(max_length=100)
    nombre_edificio = models.CharField(max_length=100)
    piso_edificio = models.CharField(max_length=100)
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE)

# ESTATICO
class CorteAcademico(models.Model):
    id_corte_academico = models.AutoField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

# ESTATICO
class VerificacionCodigo(models.Model):
    id_codigo = models.AutoField(primary_key=True)
    cedula_identidad = models.CharField(max_length=12)
    token = models.CharField(null=True, blank=True)
    codigo = models.CharField(max_length=10)
    creado = models.DateTimeField()
    intentos = models.PositiveIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    activo = models.IntegerField()
    descripcion = models.CharField(max_length=100)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

# ESTATICO
class PlanEspecial(models.Model):
    id_plan_especial = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

# ESTATICO
class Autoridades(models.Model):
    id_autoridad = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula_identidad = models.CharField(max_length=15, unique=True)
    genero = models.CharField(max_length=50)
    cargo = models.CharField(max_length=100)
    resolucion = models.CharField(max_length=100, unique=True)

# ESTATICO
class Bitacora(models.Model):
    id_bitacora = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=50)
    fecha_hora = models.DateTimeField()
    accion = models.CharField(max_length=100)

# ESTATICO
class Materia(models.Model):
    id_materia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    tipo_materia = models.CharField(max_length=100)
    trayecto = models.CharField(max_length=10)
    recuperacion = models.CharField(max_length=100)
    id_pnf = models.ForeignKey(Pnf, models.CASCADE, db_column='id_pnf')

# ESTATICO
class PeriodoAcademico(models.Model):
    id_periodo_academico = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# ESTATICO
class CalendarioAcademico(models.Model):
    id_fecha_academica = models.AutoField(primary_key=True)
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    activo = models.BooleanField(default=True) 

# ESTATICO
class PeriodoMateria(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)

# ESTATICO
class CalendarioMateria(models.Model):
    calendario = models.ForeignKey(CalendarioAcademico, on_delete=models.CASCADE)
    periodo_materia = models.ForeignKey(PeriodoMateria, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["calendario", "periodo_materia"],
                name="uq_calendario_periodo_materia"
            )
        ]

# ESTATICO
class SeccionAcademica(models.Model):
    id_seccion = models.AutoField(primary_key=True)
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE)
    id_pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE)
    id_aula = models.ForeignKey(AulaAcademica, on_delete=models.CASCADE)
    trayecto = models.CharField(max_length=10)
    turno = models.CharField(max_length=20)
    seccion = models.CharField(max_length=5)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

# ESTATICO
class HorarioAcademica(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE)
    id_pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE)
    id_periodo_academico = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)
    id_aula = models.ForeignKey(AulaAcademica, on_delete=models.CASCADE)
    trayecto = models.CharField(max_length=10)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    turno_academico = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

# ESTATICO
class ModeloDinamico(models.Model):
    nombre_modelo = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre_modelo}"
    
# ESTATICO
class CampoModelo(models.Model):
    modelo = models.ForeignKey(ModeloDinamico, on_delete=models.CASCADE, related_name="campos")
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=30,
        choices=[
            ("AutoField", "AutoField"),
            ("CharField", "CharField"),
            ("TextField", "TextField"),
            ("EmailField", "EmailField"),
            ("IntegerField", "IntegerField"),
            ("PositiveIntegerField", "PositiveIntegerField"),
            ("DecimalField", "DecimalField"),
            ("FloatField", "FloatField"),
            ("DateField", "DateField"),
            ("DateTimeField", "DateTimeField"),
            ("TimeField", "TimeField"),
            ("BooleanField", "BooleanField"),
            ("ForeignKey", "ForeignKey"),
            ("OneToOneField", "OneToOneField"),
            ("FileField", "FileField"),
        ]
    )
    max_length = models.PositiveIntegerField(blank=True, null=True)
    upload_to = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    null = models.BooleanField(default=False)
    blank = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    primary_key = models.BooleanField(default=False)
    relacion = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
    
#ACTUALIZACION / PROPUESTA

class RolAcademico(models.Model): # Modelo creado para no redundar en datos de 3 usuarios
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE)
    pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Estudiante(RolAcademico):
    id_estudiante = models.AutoField(primary_key=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "nucleo", "pnf"],
                name="uq_estudiante_usuario_nucleo_pnf"
            )
        ]

    def __str__(self):
        return f"{self.usuario}"


class Docente(RolAcademico):
    id_docente = models.AutoField(primary_key=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "nucleo", "pnf"],
                name="uq_docente_usuario_nucleo_pnf"
            )
        ]

    def __str__(self):
        return f"{self.usuario}"


class CoordinadorPNF(RolAcademico):
    id_coordinador = models.AutoField(primary_key=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "nucleo", "pnf"],
                name="uq_coordinadorpnf_usuario_nucleo_pnf"
            )
        ]
    
    def __str__(self):
        return f"{self.usuario}"

class ControlEstudio(models.Model):
    id_control = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "nucleo"],
                name="uq_control_usuario_nucleo"
            )
        ]

    def __str__(self):
        return f"{self.usuario}"


class DirectorGeneral(models.Model):
    id_director = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario"],
                name="uq_director_usuario"
            )
        ]

    def __str__(self):
        return f"{self.usuario}"