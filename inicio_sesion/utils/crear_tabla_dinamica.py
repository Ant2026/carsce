from django.db import connection, models
import re

def crear_tabla_dinamica(modelo_dinamico):

    nombre_tabla = (modelo_dinamico.nombre_modelo or "").strip()

    if not nombre_tabla:
        return "Debe indicar un nombre para el modelo."

    nombre_tabla = nombre_tabla.lower()

    # Nombre de la clase dinámica
    nombre_clase = modelo_dinamico.nombre_modelo.capitalize()


    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS(
                SELECT FROM information_schema.tables
                WHERE table_name=%s
            )
            """,
            [nombre_tabla]
        )

        if cursor.fetchone()[0]:
            return False


    campos = {}

    print(
        "CAMPOS RECIBIDOS:",
        list(
            modelo_dinamico.campos.values(
                "nombre",
                "tipo",
                "max_length",
                "null",
                "blank",
                "unique",
                "primary_key"
            )
        )
    )


    for campo in modelo_dinamico.campos.all():

        opciones = {
            "null": campo.null,
            "blank": campo.blank,
            "unique": campo.unique,
            "primary_key": campo.primary_key
        }


        if campo.tipo == "AutoField":

            campos[campo.nombre] = models.AutoField(
                primary_key=True
            )


        elif campo.tipo == "CharField":

            campos[campo.nombre] = models.CharField(
                max_length=campo.max_length or 100,
                **opciones
            )


        elif campo.tipo == "TextField":

            campos[campo.nombre] = models.TextField(
                **opciones
            )


        elif campo.tipo == "IntegerField":

            campos[campo.nombre] = models.IntegerField(
                **opciones
            )


        elif campo.tipo == "BooleanField":

            campos[campo.nombre] = models.BooleanField(
                default=False,
                **opciones
            )


        elif campo.tipo == "ForeignKey":

            if not campo.relacion:
                raise ValueError(
                    f"El campo {campo.nombre} necesita un modelo relacionado."
                )

            modelo_relacionado = campo.relacion.model_class()

            campos[campo.nombre] = models.ForeignKey(
                modelo_relacionado,
                on_delete=models.CASCADE,
                null=campo.null,
                blank=campo.blank,
                related_name=f"{nombre_tabla}_{campo.nombre}"
            )


        elif campo.tipo == "OneToOneField":

            if not campo.relacion:
                raise ValueError(
                    f"El campo {campo.nombre} necesita un modelo relacionado."
                )

            modelo_relacionado = campo.relacion.model_class()

            campos[campo.nombre] = models.OneToOneField(
                modelo_relacionado,
                on_delete=models.CASCADE,
                null=campo.null,
                blank=campo.blank,
                related_name=f"{nombre_tabla}_{campo.nombre}"
            )


        else:
            raise ValueError(
                f"Tipo de campo no soportado: {campo.tipo}"
            )


    modelo = type(
        nombre_clase,
        (models.Model,),
        {
            "__module__": "inicio_sesion.models",

            "Meta": type(
                "Meta",
                (),
                {
                    "db_table": nombre_tabla,
                    "app_label": "inicio_sesion"
                }
            ),

            **campos
        }
    )


    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(modelo)


    print("TABLA CREADA:", nombre_tabla)

    return True
def eliminar_tabla_dinamica(modelo_dinamico):
    nombre_tabla = (modelo_dinamico.nombre_modelo or "").strip()

    # Validar que tenga nombre
    if not nombre_tabla:
        raise ValueError(
            "Debe indicar un nombre para el modelo."
        )

    nombre_tabla = nombre_tabla.lower()

    # Validar nombre seguro para SQL
    if not re.fullmatch(r"[a-z][a-z0-9_]*", nombre_tabla):
        raise ValueError(
            "El nombre de la tabla no es válido."
        )

    with connection.cursor() as cursor:

        # Verificar si existe la tabla
        cursor.execute(
            """
            SELECT EXISTS(
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            );
            """,
            [nombre_tabla]
        )

        existe = cursor.fetchone()[0]

        if not existe:
            raise ValueError(
                f"La tabla '{nombre_tabla}' no existe."
            )

        # Eliminar tabla
        cursor.execute(
            f'DROP TABLE "{nombre_tabla}" CASCADE;'
        )

    return True