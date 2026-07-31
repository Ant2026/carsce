from django import forms
from .models import Usuario, Contacto, Pnf, Nucleos, PNFNucleo, PeriodoAcademico, Cuenta, ModeloDinamico, CampoModelo
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re
from django.db import models, connection

PALABRAS_RESERVADAS = {
    "select",
    "table",
    "group",
    "order",
    "from",
    "where",
    "user",
}

TIPOS_VALIDOS = {
    "AutoField",
    "CharField",
    "TextField",
    "EmailField",
    "IntegerField",
    "PositiveIntegerField",
    "DecimalField",
    "FloatField",
    "DateField",
    "DateTimeField",
    "TimeField",
    "BooleanField",
    "ForeignKey",
    "OneToOneField",
    "FileField",
}

TIPOS_PK = {
    "AutoField",
    "CharField",
    "IntegerField",
}

TIPOS_CON_LONGITUD = {
    "CharField",
    "FileField",
}

class ModeloDinamicoAdminForm(forms.ModelForm):
    class Meta:
        model = ModeloDinamico
        fields = "__all__"
        widgets = {
            "nombre_modelo": forms.TextInput(
                attrs={
                    "maxlength": 63,
                    "autocomplete": "off",
                }
            ),
            "upload_to": forms.TextInput(
                attrs={
                    "maxlength": 100,
                    "autocomplete": "off",
                    "placeholder": "Ejemplo: documentos_estudiante/"
                }
            ),
        }

    def clean_nombre_modelo(self):
        nombre = (self.cleaned_data.get("nombre_modelo") or "").strip().lower()
        print(f"Nombre recibido: '{nombre}'")
        if not nombre:
            raise forms.ValidationError(
                "Debe indicar un nombre para el modelo."
            )

        if not re.fullmatch(r"[A-Za-z][A-Za-z_]*", nombre):
            raise forms.ValidationError(
                "El nombre del modelo solo puede contener letras y '_'."
            )

        if nombre in PALABRAS_RESERVADAS:
            raise forms.ValidationError(
                "Ese nombre está reservado por SQL."
            )

        if len(nombre) > 63:
            raise forms.ValidationError(
                "El nombre del modelo es demasiado largo."
            )
        
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS(
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                )
                """,
                [nombre]
            )

            if cursor.fetchone()[0]:
                raise forms.ValidationError(
                    "Ya existe una tabla con ese nombre."
                )
            
        return nombre

class CampoModeloAdminForm(forms.ModelForm):
    class Meta:
        model = CampoModelo
        fields = "__all__"
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "maxlength": 63,
                    "autocomplete": "off",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        nombre = (cleaned_data.get("nombre") or "").strip().lower()
        tipo = cleaned_data.get("tipo")
        relacion = cleaned_data.get("relacion")
        max_length = cleaned_data.get("max_length")
        primary_key = cleaned_data.get("primary_key")
        null = cleaned_data.get("null")
        blank = cleaned_data.get("blank")
        unique = cleaned_data.get("unique")
        upload_to = (cleaned_data.get("upload_to") or "").strip()

        if not nombre:
            raise forms.ValidationError(
                "Debe indicar un nombre para el campo."
            )

        if len(nombre) > 63:
            raise forms.ValidationError(
                "El nombre del campo es demasiado largo."
            )

        if not re.fullmatch(r"[A-Za-z][A-Za-z_]*", nombre):
            raise forms.ValidationError(
                "El nombre del campo solo puede contener letras y '_'."
            )

        if nombre in PALABRAS_RESERVADAS:
            raise forms.ValidationError(
                f"'{nombre}' es una palabra reservada."
            )

        if tipo not in TIPOS_VALIDOS:
            raise forms.ValidationError(
                f"El tipo '{tipo}' no está soportado."
            )

        if tipo == "AutoField" and max_length:
            raise forms.ValidationError(
                "AutoField no permite longitud."
            )
        
        if tipo == "CharField":
            if max_length is None or max_length <= 0:
                raise forms.ValidationError(
                    "Debe indicar un max_length mayor que cero."
                )

        if tipo not in TIPOS_CON_LONGITUD and max_length:
            raise forms.ValidationError(
                f"El tipo '{tipo}' no permite max_length."
            )
    
        # Validar relaciones
        if tipo not in ("ForeignKey", "OneToOneField") and relacion:
            raise forms.ValidationError(
                "Solo ForeignKey y OneToOneField pueden tener relaciones."
            )

        if tipo in ("ForeignKey", "OneToOneField"):

            if relacion is None:
                raise forms.ValidationError(
                    "Debe seleccionar un modelo relacionado."
                )

            modelo = relacion.model_class()

            if modelo is None:
                raise forms.ValidationError(
                    "La relación seleccionada no es válida."
                )

            if not issubclass(modelo, models.Model):
                raise forms.ValidationError(
                    "La relación no corresponde a un modelo de Django."
                )

            if primary_key:
                raise forms.ValidationError(
                    "Una relación no puede ser llave primaria."
                )

            if tipo == "ForeignKey" and unique:
                raise forms.ValidationError(
                    "ForeignKey no puede tener unique=True. "
                    "Use OneToOneField."
                )

        if tipo != "FileField" and upload_to:
            raise forms.ValidationError(
                "Solo FileField puede utilizar upload_to."
            )
            
        if tipo == "FileField":
            
            if not upload_to:
                raise forms.ValidationError(
                    "Debe indicar la ruta donde se almacenarán los archivos."
                )

            if max_length and max_length <= 0:
                raise forms.ValidationError(
                    "max_length debe ser mayor que cero."
                )

            if not re.fullmatch(r"[A-Za-z0-9_]+(/[\w]+)*/", upload_to):
                raise forms.ValidationError(
                    "La ruta debe tener formato carpeta/subcarpeta/."
                )
            
        if primary_key:

            if tipo not in TIPOS_PK:
                raise forms.ValidationError(
                    f"El tipo '{tipo}' no puede ser llave primaria."
                )

            if null:
                raise forms.ValidationError(
                    "Una llave primaria no puede aceptar NULL."
                )

            if blank:
                raise forms.ValidationError(
                    "Una llave primaria no puede estar vacía."
                )

        return cleaned_data
    
class UsuarioAdminForm(forms.ModelForm):
    GENERO_CHOICES = [
        ('', 'Seleccione el Genero'),
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    ]
    ESTADO_CIVIL_CHOICES = [
        ('', 'Seleccione el Estado Civil'),
        ('Soltero/a', 'Soltero/a'),
        ('Casado/a', 'Casado/a'),
        ('Viudo/a', 'Viudo/a'),
        ('Divorciado/a', 'Divorciado/a'),
    ]
    NACIONALIDAD_CHOICES = [
        ('', 'Seleccione'),
        ('V', 'V'),
        ('E', 'E'),
    ]
    
    nacionalidad = forms.ChoiceField(
        choices=NACIONALIDAD_CHOICES,
        widget=forms.Select(attrs={
            'id': 'nacionalidad',
            'class': 'inline-select'
        })
    )

    cedula_identidad = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'cedula_identidad',
            'class': 'inline-input',
        })
    )
    genero = forms.ChoiceField(
        choices=GENERO_CHOICES
    )
    estado_civil = forms.ChoiceField(
        choices=ESTADO_CIVIL_CHOICES
    )

    def clean_nombres(self):
        nombres = self.cleaned_data['nombres'].strip()

        if len(nombres) < 3:
            raise ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )

        if len(nombres) > 30:
            raise ValidationError(
                "El nombre no puede superar los 30 caracteres."
            )

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', nombres):
            raise ValidationError(
                "El nombre solo puede contener letras."
            )
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data['apellidos'].strip()

        if len(apellidos) < 3:
            raise ValidationError(
                "El apellido debe tener al menos 3 caracteres."
            )

        if len(apellidos) > 30:
            raise ValidationError(
                "El apellido no puede superar los 30 caracteres."
            )

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', apellidos):
            raise ValidationError(
                "El apellido solo puede contener letras."
            )
        return apellidos

    def clean_cedula_identidad(self):
        cedula = self.cleaned_data['cedula_identidad'].strip()
        nacionalidad = self.cleaned_data.get('nacionalidad')

        if not cedula.isdigit():
            raise ValidationError(
                "La cédula solo puede contener números."
            )
        if nacionalidad == "V":
            if len(cedula) < 7 or len(cedula) > 8:
                raise ValidationError(
                    "La cédula venezolana debe tener entre 7 y 8 dígitos."
                )
        elif nacionalidad == "E":
            if len(cedula) < 10 or len(cedula) > 11:
                raise ValidationError(
                    "La cédula de extranjero debe tener entre 10 y 11 dígitos."
                )
        return cedula
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.cedula_identidad:
            if "-" in self.instance.cedula_identidad:
                nacionalidad, cedula = self.instance.cedula_identidad.split("-", 1)

                self.fields['nacionalidad'].initial = nacionalidad
                self.fields['cedula_identidad'].initial = cedula 

class CredencialesUsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = "__all__"

    usuario = forms.CharField(
        widget=forms.TextInput(attrs={
            "id": "id_usuario",
            "class": "inline-input",
            "placeholder": "Nombre de usuario",
            "required": True,
            "autocomplete": "off",
        })
    )

    clave = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "id": "id_clave",
            "class": "inline-input",
            "placeholder": "Contraseña",
            "required": True,
            "autocomplete": "off",
        })
    )

    def clean_nombre_usuario(self):
        usuario = self.cleaned_data['usuario'].strip()

        if len(usuario) < 4:
            raise forms.ValidationError(
                "El nombre de usuario debe tener al menos 4 caracteres."
            )

        if len(usuario) > 160:
            raise forms.ValidationError(
                "El nombre de usuario es demasiado largo."
            )

        existe = Cuenta.objects.filter(usuario=usuario)

        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)

        if existe.exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")

        return usuario

    def clean_clave(self):
        clave = self.cleaned_data['clave']

        if not clave.startswith('pbkdf2_'):
            if len(clave) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
            
        return clave

    def save(self, commit=True):
        cuenta = super().save(commit=False)

        clave = self.cleaned_data.get("clave")

        if clave and not clave.startswith("pbkdf2_"): # Solo encripta si es una clave nueva
            cuenta.clave = make_password(clave)

        if commit:
            cuenta.save()

        return cuenta

class PNFNucleoAdminForm(forms.ModelForm):
    id_pnf = forms.ModelChoiceField(queryset=Pnf.objects.all(), label='PNF')
    id_nucleo = forms.ModelChoiceField(queryset=Nucleos.objects.all(), label='Núcleo')

    class Meta:
        model = PNFNucleo
        fields = '__all__'
    
class PnfAdminForm(forms.ModelForm):

    PERIODO_ACADEMICO_CHOICES = [
        ("", "Elije el Periodo Académico"),
        ("Trimestre", "Trimestre"),
        ("Semestre", "Semestre"),
    ]

    periodo_academico = forms.ChoiceField(
        choices=PERIODO_ACADEMICO_CHOICES,
        required=False
    )

    class Meta:
        model = Pnf
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()

        if len(nombre) < 5:
            raise forms.ValidationError(
                "El nombre del PNF debe tener al menos 5 caracteres."
            )

        return nombre

class NucleoAdminForm(forms.ModelForm):

    class Meta:
        model = Nucleos
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()

        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre del núcleo debe tener al menos 3 caracteres."
            )

        return nombre

# class PerfilAdminForm(forms.ModelForm):
#     class Meta:
#         model = Perfiles
#         fields = "__all__"

#     def clean_nombre(self):
#         nombre = self.cleaned_data['nombre'].strip()

#         if len(nombre) < 3:
#             raise forms.ValidationError(
#                 "El nombre del perfil debe tener al menos 3 caracteres."
#             )

#         return nombre

# class PeriodoAcademicoAdminForm(forms.ModelForm):
#     class Meta:
#         model = Perfiles
#         fields = "__all__"

#     def clean_nombre(self):
#         nombre = self.cleaned_data['nombre'].strip()

#         if len(nombre) < 3:
#             raise forms.ValidationError(
#                 "El nombre del perfil debe tener al menos 3 caracteres."
#             )

#         return nombre
    