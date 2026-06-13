from django.contrib import admin
from .models import Usuario, Contacto, Pnf, Nucleos, Perfiles, PNFNucleo, GacetaOficial, UsuarioAsignacion
from django import forms
from django.contrib.auth.hashers import make_password
from django.forms import PasswordInput

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
        ('', 'N'),
        ('V', 'V'),
        ('E', 'E'),
    ]

    nacionalidad = forms.ChoiceField(
        choices=NACIONALIDAD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'inline-select'
        })
    )

    cedula_identidad = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'inline-input',
            'maxlength': '9'
        })
    )

    clave = forms.CharField(
        widget=forms.PasswordInput(render_value=True)
    )

    genero = forms.ChoiceField(
        choices=GENERO_CHOICES
    )

    estado_civil = forms.ChoiceField(
        choices=ESTADO_CIVIL_CHOICES
    )

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


class PNFNucleoAdminForm(forms.ModelForm):

    class Meta:
        model = PNFNucleo
        fields = '__all__'

    id_pnf = forms.ModelChoiceField(queryset=Pnf.objects.all(), label='PNF')
    id_nucleo = forms.ModelChoiceField(queryset=Nucleos.objects.all(), label='Núcleo')

class PNFNucleoAdmin(admin.ModelAdmin):
    form = PNFNucleoAdminForm

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
                'nombre_usuario',
                'clave',
            )
        }),
    )

    search_fields = (
        'nombres',
        'apellidos',
        'cedula_identidad',
        'nombre_usuario'
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

        if obj.clave and not obj.clave.startswith('pbkdf2_'):
            obj.clave = make_password(obj.clave)

        super().save_model(request, obj, form, change)
    
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

class UsuarioAsignacionAdminForm(forms.ModelForm):

    class Meta:
        model = UsuarioAsignacion
        fields = "__all__"

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

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pnf)
admin.site.register(Nucleos)
admin.site.register(Perfiles)

admin.site.register(
    PNFNucleo,
    PNFNucleoAdmin
)

admin.site.register(
    UsuarioAsignacion,
    UsuarioAsignacionAdmin
)