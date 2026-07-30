from django.db import migrations

PERIODOS_ACADEMICOS = [
    {"nombre": "Inicial"},
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

PERFILES = [
    {"perfil": "Director General"},
    {"perfil": "Encargado de Control de Estudio"},
    {"perfil": "Coordinador de PNF"},
    {"perfil": "Docente"},
    {"perfil": "Estudiante"},
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

def crear_datos(apps, schema_editor):
    Perfil = apps.get_model("inicio_sesion", "Perfiles")
    Nucleo = apps.get_model("inicio_sesion", "Nucleos")
    PeriodoAcademico = apps.get_model("inicio_sesion", "PeriodoAcademico")
    PNFNucleo = apps.get_model("inicio_sesion", "PNFNucleo")
    Pnf = apps.get_model("inicio_sesion", "Pnf")

    for perfil in PERFILES:
        Perfil.objects.get_or_create(
            perfil=perfil["perfil"]
        )

    for nucleo in NUCLEOS:
        Nucleo.objects.get_or_create(
            municipio=nucleo["municipio"],
            defaults={
                "direccion": nucleo["direccion"]
            }
        )

    for periodo in PERIODOS_ACADEMICOS:
        PeriodoAcademico.objects.get_or_create(
            nombre=periodo["nombre"]
        )

    for datos in PNF:
        Pnf.objects.get_or_create(
            codigo=datos["codigo"],
            defaults={
                "pnf": datos["pnf"],
                "periodo_academico": datos["periodo_academico"],
            }
        )

    for relacion in PNF_NUCLEO:
        nucleo = Nucleo.objects.get(
            municipio=relacion["municipio"]
        )

        pnf = Pnf.objects.get(
            codigo=relacion["codigo"]
        )

        PNFNucleo.objects.get_or_create(
            id_nucleo=nucleo,
            id_pnf=pnf
        )

def eliminar_datos(apps, schema_editor):
    Perfil = apps.get_model("inicio_sesion", "Perfiles")
    Nucleo = apps.get_model("inicio_sesion", "Nucleos")
    PeriodoAcademico = apps.get_model("inicio_sesion", "PeriodoAcademico")
    PNFNucleo = apps.get_model("inicio_sesion", "PNFNucleo")
    Pnf = apps.get_model("inicio_sesion", "Pnf")

    Perfil.objects.filter(
        perfil__in=[perfil["perfil"] for perfil in PERFILES]
    ).delete()

    Nucleo.objects.filter(
        municipio__in=[nucleo["municipio"] for nucleo in NUCLEOS]
    ).delete()

    PeriodoAcademico.objects.filter(
        nombre__in=[periodo["nombre"] for periodo in PERIODOS_ACADEMICOS]
    ).delete()

    for relacion in PNF_NUCLEO:
        nucleo = Nucleo.objects.get(
            municipio=relacion["municipio"]
        )

        pnf = Pnf.objects.get(
            codigo=relacion["codigo"]
        )

        PNFNucleo.objects.filter(
            id_nucleo=nucleo,
            id_pnf=pnf
        ).delete()

    for pnf_nucleo in PNF_NUCLEO:
        PNFNucleo.objects.get_or_create(
            id_nucleo=pnf_nucleo["id_nucleo"],
            defaults={
                "id_pnf": pnf["id_pnf"],
            }
        )

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