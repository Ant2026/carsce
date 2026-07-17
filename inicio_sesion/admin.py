from django.contrib import admin
from .models import Usuario, Contacto, CredencialesUsuario, Pnf, Nucleos, Perfiles, PNFNucleo, GacetaOficial, UsuarioAsignacion, PeriodoAcademico
from django import forms
from django.contrib.auth.hashers import make_password
from django.forms import PasswordInput
from django.core.exceptions import ValidationError
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

class ContactoInline(admin.StackedInline):
    model = Contacto
    can_delete = False
    extra = 1
    exclude = ('id_contacto',)

class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm

    inlines = [ContactoInline]

    fieldsets = (
        ('Datos de Identidad', {
            'fields': (
                'nombres',
                'apellidos',
                ('nacionalidad', 'cedula_identidad'),
                'genero',
                'estado_civil',
            )
        }),
    )

    search_fields = (
        'nombres',
        'apellidos',
        'cedula_identidad',
    )

    class Media:
        js = (
            'Funcionalidades/password_admin.js',
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        for field in form.base_fields.values():
            field.widget.attrs['autocomplete'] = 'off'

        return form

    def save_model(self, request, obj, form, change):

        nacionalidad = form.cleaned_data.get('nacionalidad')
        cedula = form.cleaned_data.get('cedula_identidad')

        if nacionalidad and cedula:
            obj.cedula_identidad = f"{nacionalidad}-{cedula}"

        super().save_model(request, obj, form, change)


class CredencialesUsuarioAdminForm(forms.ModelForm):

    class Meta:
        model = CredencialesUsuario
        fields = "__all__"

    def clean_nombre_usuario(self):

        usuario = self.cleaned_data['nombre_usuario'].strip()

        if len(usuario) < 4:
            raise forms.ValidationError(
                "El nombre de usuario debe tener al menos 4 caracteres."
            )

        if len(usuario) > 160:
            raise forms.ValidationError(
                "El nombre de usuario es demasiado largo."
            )

        existe = CredencialesUsuario.objects.filter(
            nombre_usuario=usuario
        )

        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)

        if existe.exists():
            raise forms.ValidationError(
                "Este nombre de usuario ya existe."
            )

        return usuario

    def clean_clave(self):

        clave = self.cleaned_data['clave']

        # Solo validar cuando no esté hasheada
        if not clave.startswith('pbkdf2_'):

            if len(clave) < 8:
                raise forms.ValidationError(
                    "La contraseña debe tener al menos 8 caracteres."
                )

        return clave
    
class CredencialesUsuarioAdmin(admin.ModelAdmin):

    form = CredencialesUsuarioAdminForm

    list_display = (
        'nombre_usuario',
        'id_asignacion',
    )

    search_fields = (
        'nombre_usuario',
    )





class PNFNucleoAdminForm(forms.ModelForm):
    id_pnf = forms.ModelChoiceField(queryset=Pnf.objects.all(), label='PNF')
    id_nucleo = forms.ModelChoiceField(queryset=Nucleos.objects.all(), label='Núcleo')

    class Meta:
        model = PNFNucleo
        fields = '__all__'

class PNFNucleoAdmin(admin.ModelAdmin):
    form = PNFNucleoAdminForm


class UsuarioAsignacionAdminForm(forms.ModelForm):

    class Meta:
        model = UsuarioAsignacion
        fields = "__all__"

    id_usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.all(),
        label="Usuario"
    )

    id_perfil = forms.ModelChoiceField(
        queryset=Perfiles.objects.all(),
        label="Perfil"
    )

    id_nucleo = forms.ModelChoiceField(
        queryset=Nucleos.objects.all(),
        label="Núcleo",
        required=False
    )

    id_pnf = forms.ModelChoiceField(
        queryset=Pnf.objects.all(),
        label="PNF",
        required=False
    )

    def clean(self):

        cleaned_data = super().clean()

        nucleo = cleaned_data.get("id_nucleo")
        pnf = cleaned_data.get("id_pnf")

        if nucleo and pnf:

            existe = PNFNucleo.objects.filter(
                id_nucleo=nucleo,
                id_pnf=pnf
            ).exists()

            if not existe:
                raise forms.ValidationError(
                    "El PNF seleccionado no pertenece al núcleo indicado."
                )

        return cleaned_data

class UsuarioAsignacionAdmin(admin.ModelAdmin):
    form = UsuarioAsignacionAdminForm

    list_display = (
        "id_usuario",
        "id_perfil",
        "id_nucleo",
        "id_pnf",
    )

    search_fields = (
        "id_usuario__nombres",
        "id_usuario__apellidos",
        "id_usuario__cedula_identidad",
    )

    list_filter = (
        "id_perfil",
        "id_nucleo",
        "id_pnf",
    )
 

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

class PnfAdmin(admin.ModelAdmin):
    form = PnfAdminForm


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

class NucleoAdmin(admin.ModelAdmin):
    form = NucleoAdminForm


class PerfilAdminForm(forms.ModelForm):

    class Meta:
        model = Perfiles
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()

        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre del perfil debe tener al menos 3 caracteres."
            )

        return nombre

class PerfilAdmin(admin.ModelAdmin):
    form = PerfilAdminForm


@admin.register(GacetaOficial)
class GacetaOficialAdmin(admin.ModelAdmin):

    list_display = (
        'gaceta_oficial',
        'fecha_gaceta_oficial',
        'id_usuario'
    )

class PeriodoAcademicoAdminForm(forms.ModelForm):
    class Meta:
        model = Perfiles
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()

        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre del perfil debe tener al menos 3 caracteres."
            )

        return nombre
    
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    form = PeriodoAcademicoAdminForm

admin.site.register(PeriodoAcademico, PeriodoAcademicoAdmin)

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pnf, PnfAdmin)
admin.site.register(Nucleos, NucleoAdmin)
admin.site.register(Perfiles, PerfilAdmin)

admin.site.register(CredencialesUsuario, CredencialesUsuarioAdmin)
admin.site.register(PNFNucleo, PNFNucleoAdmin)
admin.site.register(UsuarioAsignacion, UsuarioAsignacionAdmin)