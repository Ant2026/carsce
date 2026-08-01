from django import forms
from .models import Usuario, Contacto, Pnf, Nucleos, PNFNucleo, PeriodoAcademico, Cuenta
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re
    
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
    