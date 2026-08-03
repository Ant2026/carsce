from django.db import migrations

PERIODOS_ACADEMICOS = [
    {"nombre": "Inicial Trimestre"},
    {"nombre": "Inicial Semestre"},
    {"nombre": "Reparación"},
    {"nombre": "Tramo I"},
    {"nombre": "Tramo II"},
    {"nombre": "Tramo III"},
    {"nombre": "Semestre I"},
    {"nombre": "Semestre II"},
]

NUCLEOS = [
    {"municipio": "Barinas", "direccion": "Dirección Barinas"},
    {"municipio": "Barinitas", "direccion": "Dirección Barinitas"},
    {"municipio": "Socopo", "direccion": "Dirección Socopó"},
    {"municipio": "Pedraza", "direccion": "Dirección Ciudad Bolivia"},
]

PNF = [
    {"pnf": "PNF en Sistema e Informática", "codigo": "CARRE001", "periodo_academico": "Trimestre"},
    {"pnf": "PNF en Electrónica", "codigo": "CARRE002", "periodo_academico": "Trimestre"},
    {"pnf": "PNF en Mediciona Veterinaria", "codigo": "CARRE003", "periodo_academico": "Semestre"},
    {"pnf": "PNF en Electricidad", "codigo": "CARRE004", "periodo_academico": "Trimestre"},
    {"pnf": "PNF en Mecánica", "codigo": "CARRE005", "periodo_academico": "Trimestre"},
    {"pnf": "PNF en Agroalimentación", "codigo": "CARRE006", "periodo_academico": "Trimestre"},
    {"pnf": "PNF en Contrucción Civil", "codigo": "CARRE007", "periodo_academico": "Trimestre"},
    {"pnf": "PNF en Ingeniería Industrial", "codigo": "CARRE008", "periodo_academico": "Trimestre"},
]

PNF_NUCLEO = [
    {"municipio": "Barinas", "codigo": "CARRE001"},
    {"municipio": "Barinas", "codigo": "CARRE002"},
    {"municipio": "Barinas", "codigo": "CARRE003"},

    {"municipio": "Barinitas", "codigo": "CARRE004"},
    {"municipio": "Barinitas", "codigo": "CARRE005"},
    {"municipio": "Barinitas", "codigo": "CARRE006"},
    {"municipio": "Barinitas", "codigo": "CARRE007"},
    {"municipio": "Barinitas", "codigo": "CARRE008"},
    {"municipio": "Barinitas", "codigo": "CARRE001"},
    {"municipio": "Barinitas", "codigo": "CARRE003"},

    {"municipio": "Socopo", "codigo": "CARRE004"},
    {"municipio": "Socopo", "codigo": "CARRE006"},
    {"municipio": "Socopo", "codigo": "CARRE007"},
    {"municipio": "Socopo", "codigo": "CARRE001"},
    {"municipio": "Socopo", "codigo": "CARRE003"},

    {"municipio": "Pedraza", "codigo": "CARRE006"},
    {"municipio": "Pedraza", "codigo": "CARRE003"},
]

GRUPOS_ACTIVIDADES = [
    {"nombre": "Feriados"},
    {"nombre": "Contrato Colectivo"},
    {"nombre": "Días Especiales"},
    {"nombre": "Actos de Grado"},
    {"nombre": "Actividades Académicas"},
]

ACTIVIDADES = [
    # Feriados
    {"grupo": "Feriados", "actividad": "Inicio de Año"},
    {"grupo": "Feriados", "actividad": "Carnaval"},
    {"grupo": "Feriados", "actividad": "Jueves y Viernes Santo"},
    {"grupo": "Feriados", "actividad": "Declaración de Independencia"},
    {"grupo": "Feriados", "actividad": "Día del Trabajador"},
    {"grupo": "Feriados", "actividad": "Batalla de Carabobo"},
    {"grupo": "Feriados", "actividad": "Día de la Independencia"},
    {"grupo": "Feriados", "actividad": "Natalicio de Simón Bolívar"},
    {"grupo": "Feriados", "actividad": "Día del Profesor Universitario"},
    {"grupo": "Feriados", "actividad": "Noche Buena"},
    {"grupo": "Feriados", "actividad": "Navidad"},
    {"grupo": "Feriados", "actividad": "Fin de Año"},

    # Contrato Colectivo
    {"grupo": "Contrato Colectivo", "actividad": "Período de Vacaciones"},
    {"grupo": "Contrato Colectivo", "actividad": "Asueto Carnaval"},
    {"grupo": "Contrato Colectivo", "actividad": "Asueto Semana Santa"},

    # Días Especiales
    {"grupo": "Días Especiales", "actividad": "Muerte de José Félix Ribas"},
    {"grupo": "Días Especiales", "actividad": "Semana Aniversario de la UPT"},
    {"grupo": "Días Especiales", "actividad": "Natalicio José Félix Ribas"},
    {"grupo": "Días Especiales", "actividad": "Día del Estudiante"},
]

def crear_datos(apps, schema_editor):
    Nucleo = apps.get_model("inicio_sesion", "Nucleos")
    PeriodoCargarNotas = apps.get_model("inicio_sesion", "PeriodoCargarNotas")
    carrera = apps.get_model("inicio_sesion", "Pnf")
    PNFNucleo = apps.get_model("inicio_sesion", "PNFNucleo")    
    GrupoActividad = apps.get_model("inicio_sesion", "GrupoActividad")
    Actividad = apps.get_model("inicio_sesion", "Actividad")

    # Núcleos
    for nucleo in NUCLEOS:
        Nucleo.objects.get_or_create(
            municipio=nucleo["municipio"],
            defaults={
                "direccion": nucleo["direccion"],
            },
        )

    # Períodos para carga de notas
    for periodo in PERIODOS_ACADEMICOS:
        PeriodoCargarNotas.objects.get_or_create(
            nombre=periodo["nombre"]
        )

    # PNF
    for datos in PNF:
        carrera.objects.get_or_create(
            codigo=datos["codigo"],
            defaults={
                "pnf": datos["pnf"],
                "periodo_academico": datos["periodo_academico"],
            },
        )

    # Relación PNF - Núcleo
    for relacion in PNF_NUCLEO:
        nucleo = Nucleo.objects.get(
            municipio=relacion["municipio"]
        )

        pnf = carrera.objects.get(
            codigo=relacion["codigo"]
        )

        PNFNucleo.objects.get_or_create(
            id_nucleo=nucleo,
            id_pnf=pnf,
        )

    # Crear grupos
    for grupo in GRUPOS_ACTIVIDADES:
        GrupoActividad.objects.get_or_create(
            nombre=grupo["nombre"]
        )

    # Crear actividades
    for dato in ACTIVIDADES:
        grupo = GrupoActividad.objects.get(
            nombre=dato["grupo"]
        )

        Actividad.objects.get_or_create(
            grupo=grupo,
            nombre=dato["actividad"]
        )


def eliminar_datos(apps, schema_editor):
    Nucleo = apps.get_model("inicio_sesion", "Nucleos")
    PeriodoCargarNotas = apps.get_model("inicio_sesion", "PeriodoCargarNotas")
    PNFNucleo = apps.get_model("inicio_sesion", "PNFNucleo")
    Pnf = apps.get_model("inicio_sesion", "Pnf")
    GrupoActividad = apps.get_model("inicio_sesion", "GrupoActividad")
    Actividad = apps.get_model("inicio_sesion", "Actividad")

    PNFNucleo.objects.all().delete()

    Pnf.objects.filter(
        codigo__in=[p["codigo"] for p in PNF]
    ).delete()

    PeriodoCargarNotas.objects.filter(
        nombre__in=[p["nombre"] for p in PERIODOS_ACADEMICOS]
    ).delete()

    Nucleo.objects.filter(
        municipio__in=[n["municipio"] for n in NUCLEOS]
    ).delete()

    Actividad.objects.filter(
        nombre__in=[a["actividad"] for a in ACTIVIDADES]
    ).delete()

    GrupoActividad.objects.filter(
        nombre__in=[g["nombre"] for g in GRUPOS_ACTIVIDADES]
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("inicio_sesion", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            crear_datos,
            eliminar_datos
        ),
    ]