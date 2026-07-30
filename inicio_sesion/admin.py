from django.contrib import admin, messages
from django.core.management import call_command
from django.db import transaction

from .forms import ModeloDinamicoAdminForm, CampoModeloAdminForm, UsuarioAdminForm,CredencialesUsuarioAdminForm, PNFNucleoAdminForm, PnfAdminForm, NucleoAdminForm, PerfilAdminForm, PeriodoAcademicoAdminForm

from .models import Usuario, Contacto, Pnf, Nucleos, Perfiles, PNFNucleo, PeriodoAcademico, Cuenta, ModeloDinamico, CampoModelo

from .utils.crear_tabla_dinamica import crear_tabla_dinamica, eliminar_tabla_dinamica

from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

class CampoModeloInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        nombres = set()
        pk = 0
        campos_validos = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            nombre = (form.cleaned_data.get("nombre") or "").strip().lower()

            if not nombre:
                continue

            campos_validos += 1

            if nombre in nombres:
                raise ValidationError(
                    f"El campo '{nombre}' está repetido."
                )

            nombres.add(nombre)

            if form.cleaned_data.get("primary_key"):
                pk += 1

        if campos_validos == 0:
            raise ValidationError(
                "Debe crear al menos un campo."
            )

        if pk > 1:
            raise ValidationError(
                "Solo puede existir una llave primaria."
            )

class CampoModeloInline(admin.TabularInline):
    model = CampoModelo
    form = CampoModeloAdminForm
    formset = CampoModeloInlineFormSet
    extra = 1

@admin.register(ModeloDinamico)
class ModeloDinamicoAdmin(admin.ModelAdmin):

    form = ModeloDinamicoAdminForm
    inlines = [CampoModeloInline]


    @transaction.atomic
    def save_related(self, request, form, formsets, change):

        print("Entró a save_related")

        super().save_related(
            request,
            form,
            formsets,
            change
        )

        form.instance.refresh_from_db()

        # Solo crea la tabla cuando es un registro nuevo
        if not change:
            crear_tabla_dinamica(
                form.instance
            )


    @transaction.atomic
    def delete_model(self, request, obj):

        # Elimina la tabla física en PostgreSQL
        eliminar_tabla_dinamica(obj)

        # Elimina el registro en Django
        super().delete_model(
            request,
            obj
        )


    @transaction.atomic
    def delete_queryset(self, request, queryset):

        # Eliminación múltiple desde la lista del Admin
        for obj in queryset:
            eliminar_tabla_dinamica(obj)

        super().delete_queryset(
            request,
            queryset
        )

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

class PerfilAdmin(admin.ModelAdmin):
    form = PerfilAdminForm

class PeriodoAcademicoAdmin(admin.ModelAdmin):
    form = PeriodoAcademicoAdminForm

admin.site.register(PeriodoAcademico, PeriodoAcademicoAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pnf, PnfAdmin)
admin.site.register(Nucleos, NucleoAdmin)
admin.site.register(Perfiles, PerfilAdmin)
admin.site.register(Cuenta, CredencialesUsuarioAdmin)
admin.site.register(PNFNucleo, PNFNucleoAdmin)
admin.site.register(Contacto)