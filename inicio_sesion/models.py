from django.db import models
from django.contrib.auth.hashers import make_password

# Clases (Tablas) principales 

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    genero = models.CharField(max_length=50)
    cedula_identidad = models.CharField(max_length=15)
    estado_civil = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class PadresEstudiante(models.Model):
    id_representante = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula_identidad = models.CharField(max_length=15, unique=True)
    telefono = models.CharField(max_length=15)
    parentesco = models.CharField(max_length=25)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='padresEstudiante')

class Residencia(models.Model):
    id_residencia = models.AutoField(primary_key=True)
    condicion_residencia = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    parroquia = models.CharField(max_length=100)
    direccion_residencia = models.CharField(max_length=100)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='residencia')

class Contacto(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    telefono_suplete = models.CharField(max_length=15, null=True, blank=True)
    telefono_personal = models.CharField(max_length=15, null=True, blank=True)
    correo_electronico = models.EmailField(max_length=100, unique=True)
    correo_alternativo = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='contacto')

class Nacimiento(models.Model):
    id_nacimiento = models.AutoField(primary_key=True)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    parroquia = models.CharField(max_length=100)
    direccion_nacimiento = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='nacimiento')

class Pnf(models.Model):
    id_pnf = models.AutoField(primary_key=True)
    pnf = models.CharField(max_length=50)
    codigo = models.CharField(max_length=40)
    periodo_academico = models.CharField(max_length=40, null=True, blank=True)
    
    def __str__(self):
        return self.pnf

class Nucleos(models.Model):
    id_nucleo = models.AutoField(primary_key=True)
    municipio = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)

    def __str__(self):
        return self.municipio
    
class Perfiles(models.Model):
    id_pefil = models.AutoField(primary_key=True)
    perfil = models.CharField(max_length=50)

    def __str__(self):
        return self.perfil

# Clases (Tablas) relacionadas usuario general

class PNFNucleo(models.Model):
    id_pnf_nucleo = models.AutoField(primary_key=True)
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE, db_column='id_nucleo')
    id_pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE, db_column='id_pnf')

class UsuarioAsignacion(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_perfil = models.ForeignKey(Perfiles, on_delete=models.CASCADE)
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE, null=True, blank=True)
    id_pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE, null=True, blank=True)

class CredencialesUsuario(models.Model):
    nombre_usuario = models.CharField(max_length=160)
    clave = models.CharField(max_length=160)
    id_asignacion = models.ForeignKey(UsuarioAsignacion, on_delete=models.CASCADE, related_name='perfil')

    def save(self, *args, **kwargs):
        if self.clave and not self.clave.startswith('pbkdf2_'):
            self.clave = make_password(self.clave)
        super().save(*args, **kwargs)

# Clases (Tablas) para Docentes, Coordinadores de PNFs, Directores Generales y Control de estudio

class DatosPreofesion(models.Model):
    id_dato_academico = models.AutoField(primary_key=True)
    profesion_pregrado = models.CharField(max_length=150)
    universidad_egreso_pregrado = models.CharField(max_length=150)
    pais_profesion_pregrado = models.CharField(max_length=150)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='profesional')

class GacetaOficial(models.Model):
    id_gaceta = models.AutoField(primary_key=True)
    gaceta_oficial = models.CharField(max_length=150)
    fecha_gaceta_oficial = models.DateField()
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='gaceta')

# Clases (Tablas) para Estudiantes

class Discapacidad(models.Model):
    id_discapacidad = models.AutoField(primary_key=True)
    codigo_carnet_discapacidad = models.CharField(max_length=50)
    nro_registro_medico = models.CharField(max_length=5)
    tipo_discapacidad = models.CharField(max_length=20)
    grado_discapacidad = models.CharField(max_length=50)
    causa_discapacidad = models.CharField(max_length=50)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='discapacidad')

class EstatusEstudiante(models.Model):
    id_estatus_estudiante = models.AutoField(primary_key=True)
    estatus = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)
    ingreso = models.CharField(max_length=50)
    descripcion_ingreso = models.CharField(max_length=30)
    trayecto = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    id_asignacion = models.ForeignKey(UsuarioAsignacion, on_delete=models.CASCADE, related_name='estatus')

class DocumentosEstudiante(models.Model):
    id_documento = models.AutoField(primary_key=True)
    nombre_documento = models.CharField(max_length=50)
    archivo = models.FileField(upload_to="documentos_estudiante/")
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='documentos')

class InformacionSecundaria(models.Model):
    id_secundaria = models.AutoField(primary_key=True)
    tipo_institucion = models.CharField(max_length=100)
    nombre_institucion = models.CharField(max_length=100)
    fecha_grado = models.DateField()
    codigo_sni_opsu = models.CharField(max_length=100, unique=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='secundaria')

class CorteAcademico(models.Model):
    id_corte_academico = models.AutoField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

class SeccionAcademica(models.Model):
    id_seccion = models.AutoField(primary_key=True)
    seccion = models.CharField(max_length=5)

# Clases (Tablas) relacionadas para estudiantes

class SeccionEstudiante(models.Model):
    id_seccion_estudiante = models.AutoField(primary_key=True)
    id_seccion = models.ForeignKey(SeccionAcademica, on_delete=models.CASCADE, db_column='id_seccion')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_inicio = models.DateField()
    fecha_final = models.DateField(null=True, blank=True)
    
class EstudianteCorte(models.Model):
    id_estudiante_corte = models.AutoField(primary_key=True)
    id_corte_academico = models.ForeignKey(CorteAcademico, on_delete=models.CASCADE, db_column='id_corte_academico')
    id_perfil_pnf = models.ForeignKey(UsuarioAsignacion, on_delete=models.CASCADE, db_column='id_perfil_pnf')

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

#

class PlanEspecial(models.Model):
    id_plan_especial = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

class Autoridades(models.Model):
    id_autoridad = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula_identidad = models.CharField(max_length=15, unique=True)
    genero = models.CharField(max_length=50)
    cargo = models.CharField(max_length=100)
    resolucion = models.CharField(max_length=100, unique=True)

class Bitacora(models.Model):
    id_bitacora = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=50)
    fecha_hora = models.DateTimeField()
    accion = models.CharField(max_length=100)

class Materia(models.Model):
    id_materia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    tipo_materia = models.CharField(max_length=100)
    trayecto = models.CharField(max_length=100)
    recuperacion = models.CharField(max_length=100)
    id_pnf = models.ForeignKey(Pnf, models.CASCADE, db_column='id_pnf')

class MateriaAsignada(models.Model):
    id_materia_asignada = models.AutoField(primary_key=True)
    id_materia = models.ForeignKey(Materia, models.CASCADE, db_column='id_materia')
    id_asignacion = models.ForeignKey(UsuarioAsignacion, models.CASCADE, db_column='id_usuario')

class PeriodoAcademico(models.Model):
    id_periodo_academico = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class CalendarioAcademico(models.Model):
    id_fecha_academica = models.AutoField(primary_key=True)
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    activo = models.BooleanField(default=True) 

class PeriodoMateria(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)

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
    
