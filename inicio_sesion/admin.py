from django.contrib import admin
from .models import Usuario, Contacto, Pnf, Nucleos, Perfiles, UsuarioPerfil, PerfilesPnf, UsuarioNucleo, PNFNucleo
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


class UsuarioPerfilInlineForm(forms.ModelForm):

    class Meta:
        model = UsuarioPerfil
        fields = '__all__'

    id_perfil = forms.ModelChoiceField(
        queryset=Perfiles.objects.all(),
        label='Perfil Usuario'
    )

class UsuarioPerfilInline(admin.TabularInline):
    model = UsuarioPerfil
    form = UsuarioPerfilInlineForm
    extra = 1


class UsuarioNucleoInlineForm(forms.ModelForm):

    class Meta:
        model = UsuarioNucleo
        fields = '__all__'

    id_nucleo = forms.ModelChoiceField(
        queryset=Nucleos.objects.all(),
        label='Núcleo Usuario'
    )

class UsuarioNucleoInline(admin.TabularInline):
    model = UsuarioNucleo
    form = UsuarioNucleoInlineForm
    extra = 1


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

    class Meta:
        model = Usuario
        fields = '__all__'

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

class PNFNucleoAdminForm(forms.ModelForm):

    class Meta:
        model = PNFNucleo
        fields = '__all__'

    id_pnf = forms.ModelChoiceField(queryset=Pnf.objects.all(), label='PNF')
    id_nucleo = forms.ModelChoiceField(queryset=Nucleos.objects.all(), label='Núcleo')

class PNFNucleoAdmin(admin.ModelAdmin):
    form = PNFNucleoAdminForm


class PerfilesPnfInlineForm(forms.ModelForm):

    class Meta:
        model = PerfilesPnf
        fields = '__all__'

    id_perfil_asignado = forms.ModelChoiceField(queryset=UsuarioPerfil.objects.all(), label='Usuario Perfil Asignado')
    id_pnf = forms.ModelChoiceField(queryset=Pnf.objects.all(), label='Pnf')

class PerfilesPnfAdmin(admin.ModelAdmin):
    form = PerfilesPnfInlineForm


admin.site.register(PerfilesPnf, PerfilesPnfAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pnf)
admin.site.register(Nucleos)
admin.site.register(Perfiles)
admin.site.register(PNFNucleo, PNFNucleoAdmin)