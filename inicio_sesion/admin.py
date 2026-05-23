from django.contrib import admin
from .models import Usuario, Contacto, Pnf, Nucleos, Perfiles, UsuarioPerfil, PerfilesPnf, UsuarioNucleo, PNFNucleo
from django import forms
from django.contrib.auth.hashers import make_password

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
        widget=forms.Select(attrs={'class': 'inline-select'})
    )

    cedula_identidad = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'inline-input'})
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

    class Meta:
        model = Usuario
        fields = '__all__'

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
    extra = 0

class UsuarioPerfilInline(admin.TabularInline):
    model = UsuarioPerfil
    extra = 1

class UsuarioNucleoInline(admin.TabularInline):
    model = UsuarioNucleo
    extra = 1

class PNFNucleoInline(admin.TabularInline):
    model = PNFNucleo
    extra = 1

class PnfAdmin(admin.ModelAdmin):
    inlines = [PNFNucleoInline]

    list_display = ('id_pnf', 'pnf', 'codigo')

class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm

    inlines = [ContactoInline, UsuarioPerfilInline, UsuarioNucleoInline]

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

    def save_model(self, request, obj, form, change):

        nacionalidad = form.cleaned_data.get('nacionalidad')
        cedula = form.cleaned_data.get('cedula_identidad')

        if nacionalidad and cedula:
            obj.cedula_identidad = f"{nacionalidad}-{cedula}"

        if obj.clave and not obj.clave.startswith('pbkdf2_'):
            obj.clave = make_password(obj.clave)

        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('Estilos/estilos.css',)
        }
        media = {
            'all': ('Funcionalidades/cedula_identidad.js',)
        }

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pnf, PnfAdmin)
admin.site.register(Nucleos)
admin.site.register(Perfiles)