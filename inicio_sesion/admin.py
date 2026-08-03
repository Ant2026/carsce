from django.contrib import admin

from .forms import UsuarioAdminForm, CredencialesUsuarioAdminForm, PNFNucleoAdminForm, PnfAdminForm, NucleoAdminForm

from .models import Usuario, Contacto, Pnf, Nucleos, PNFNucleo, PeriodoCargarNotas, Cuenta, Estudiante, Docente, CoordinadorPNF, ControlEstudio, DirectorGeneral

class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm
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

class CredencialesUsuarioAdmin(admin.ModelAdmin):
    form = CredencialesUsuarioAdminForm

    list_display = (
        'usuario',
    )

    search_fields = (
        'usuario',
    )

    class Media:
        css = {
            "all": ("Estilos/fontello.css", "Estilos/estilos_admin.css")
        }
        js = (
            "Funcionalidades/password_admin.js",
        )

class PNFNucleoAdmin(admin.ModelAdmin):
    form = PNFNucleoAdminForm

class PnfAdmin(admin.ModelAdmin):
    form = PnfAdminForm

class NucleoAdmin(admin.ModelAdmin):
    form = NucleoAdminForm

admin.site.register(Estudiante)
admin.site.register(Docente)
admin.site.register(CoordinadorPNF)
admin.site.register(ControlEstudio)
admin.site.register(DirectorGeneral)

admin.site.register(PeriodoCargarNotas)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pnf, PnfAdmin)
admin.site.register(Nucleos, NucleoAdmin)
admin.site.register(Cuenta, CredencialesUsuarioAdmin)
admin.site.register(PNFNucleo, PNFNucleoAdmin)
admin.site.register(Contacto)