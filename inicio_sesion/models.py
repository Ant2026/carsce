from django.db import models
from django.contrib.auth.hashers import make_password

# Clases (Tablas) principales 

class Usuario(models.Model):
    id_usuario = models.IntegerField(primary_key=True)
    nombres = models.CharField(max_length=30)
    apellidos = models.CharField(max_length=100)
    genero = models.CharField(max_length=30)
    cedula_identidad = models.CharField(max_length=12, unique=True)
    estado_civil = models.CharField(max_length=30)
    nombre_usuario = models.CharField(max_length=120)
    clave = models.CharField(max_length=120)

    def save(self, *args, **kwargs):
        if self.clave and not self.clave.startswith('pbkdf2_'):
            self.clave = make_password(self.clave)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombres

class Residencia(models.Model):
    id_residencia = models.IntegerField(primary_key=True)
    condicion_residencia = models.CharField(max_length=20)
    municipio = models.CharField(max_length=30)
    parroquia = models.CharField(max_length=30)
    direccion_residencia = models.CharField(max_length=30)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='residencia')

class Contacto(models.Model):
    id_contacto = models.IntegerField(primary_key=True)
    telefono_suplete = models.CharField(max_length=12)
    telefono_personal = models.CharField(max_length=12)
    correo_electronico = models.CharField(max_length=50, unique=True)
    correo_alternativo = models.CharField(max_length=50)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='contacto')

class Nacimiento(models.Model):
    id_nacimiento = models.IntegerField(primary_key=True)
    pais = models.CharField(max_length=30)
    estado = models.CharField(max_length=30)
    parroquia = models.CharField(max_length=30)
    direccion_nacimiento = models.CharField(max_length=30)
    fecha_nacimiento = models.DateField()
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='nacimiento')

class Pnf(models.Model):
    id_pnf = models.AutoField(primary_key=True)
    pnf = models.CharField(max_length=40)
    codigo = models.CharField(max_length=10)

    def __str__(self):
        return self.pnf

class Nucleos(models.Model):
    id_nucleo = models.AutoField(primary_key=True)
    municipio = models.CharField(max_length=40)

    def __str__(self):
        return self.municipio
    
class Perfiles(models.Model):
    id_pefil = models.AutoField(primary_key=True)
    perfil = models.CharField(max_length=40)

    def __str__(self):
        return self.perfil

# Clases (Tablas) relacionadas usuario general

class UsuarioPerfil(models.Model):
    id_perfil_asignado = models.AutoField(primary_key=True)
    id_perfil = models.ForeignKey(Perfiles, on_delete=models.CASCADE, db_column='id_perfil')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')

class PNFNucleo(models.Model):
    id_pnf_nucleo = models.AutoField(primary_key=True)
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE, db_column='id_nucleo')
    id_pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE, db_column='id_pnf')

class PerfilesPnf(models.Model):
    id_perfil_pnf = models.AutoField(primary_key=True)
    id_pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE, db_column='id_pnf')
    id_perfil_asignado = models.ForeignKey(UsuarioPerfil, on_delete=models.CASCADE, db_column='id_perfil_asignado')

class UsuarioNucleo(models.Model):
    id_usuario_nucleo = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_nucleo = models.ForeignKey(Nucleos, on_delete=models.CASCADE, db_column='id_nucleo')

# Clases (Tablas) para Docentes, Coordinadores de PNFs, Directores Generales y Control de estudio

class DatosPreofesion(models.Model):
    id_dato_academico = models.IntegerField(primary_key=True)
    profesion_pregrado = models.CharField(max_length=30)
    universidad_egreso_pregrado = models.CharField(max_length=30)
    pais_profesion_pregrado = models.CharField(max_length=10)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='profesional')

class GacetaOficial(models.Model):
    id_gaceta = models.IntegerField(primary_key=True)
    gaceta_oficial = models.CharField(max_length=10)
    fecha_gaceta_oficial = models.DateField()
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='gaceta')

# Clases (Tablas) para Estudiantes

class Discapacidad(models.Model):
    id_discapacidad = models.IntegerField(primary_key=True)
    codigo_carnet_discapacidad = models.CharField(max_length=10)
    nro_registro_medico = models.CharField(max_length=5)
    tipo_discapacidad = models.CharField(max_length=10)
    grado_discapacidad = models.CharField(max_length=20)
    causa_discapacidad = models.CharField(max_length=20)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='discapacidad')

class EstatusEstudiante(models.Model):
    id_estatus_estudiante = models.IntegerField(primary_key=True)
    estatus = models.CharField(max_length=20)
    estado = models.CharField(max_length=10)
    ingreso = models.CharField(max_length=10)
    descripcion_ingreso = models.CharField(max_length=15)
    trayecto = models.CharField(max_length=10)
    fecha_ingreso = models.DateField()
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='estatus')

class DocumentosEstudiante(models.Model):
    id_documento = models.IntegerField(primary_key=True)
    nombre_documento = models.CharField(max_length=20)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='documentos')

class InformacionSecundaria(models.Model):
    id_secundaria = models.IntegerField(primary_key=True)
    tipo_institucion = models.CharField(max_length=10)
    nombre_institucion = models.CharField(max_length=20)
    fecha_grado = models.DateField()
    codigo_sni_opsu = models.CharField(max_length=10, unique=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='secundaria')

class CorteAcademico(models.Model):
    id_corte_academico = models.IntegerField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

class SeccionAcademica(models.Model):
    id_seccion = models.IntegerField(primary_key=True)
    seccion = models.CharField(max_length=5)

# Clases (Tablas) relacionadas para estudiantes

class SeccionEstudiante(models.Model):
    id_seccion_estudiante = models.IntegerField(primary_key=True)
    id_seccion = models.ForeignKey(SeccionAcademica, on_delete=models.CASCADE, db_column='id_seccion')
    id_perfil_pnf = models.ForeignKey(PerfilesPnf, on_delete=models.CASCADE, db_column='id_perfil_pnf')
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    
class EstudianteCorte(models.Model):
    id_estudiante_corte = models.IntegerField(primary_key=True)
    id_corte_academico = models.ForeignKey(CorteAcademico, on_delete=models.CASCADE, db_column='id_corte_academico')
    id_perfil_pnf = models.ForeignKey(PerfilesPnf, on_delete=models.CASCADE, db_column='id_perfil_pnf')
    