document.addEventListener("DOMContentLoaded", () => {

    // ==========================================================
    // FECHA Y HORA EXACTA DE EJECUCIÓN
    // ==========================================================

    const FECHA_REPARACIONES = new Date(
        "2027-12-06T08:00:00"
    );

    const FECHA_ACTUALIZACION_TRAYECTOS = new Date(
        "2027-12-11T08:00:00"
    );



    const CLAVE_REPARACIONES =
        "reparaciones_2027_12_06_08_00";

    const CLAVE_TRAYECTOS =
        "actualizacion_trayectos_2027_12_11_08_00";

    function obtener_csrf_token() {

        const nombre = "csrftoken=";

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(nombre)) {

                return decodeURIComponent(
                    cookie.substring(nombre.length)
                );
            }
        }

        return "";
    }


    // ==========================================================
    // PROCESAR REPARACIONES
    // ==========================================================

    async function ejecutar_reparaciones() {

        if (
            localStorage.getItem(
                CLAVE_REPARACIONES
            ) === "true"
        ) {

            console.log(
                "Las reparaciones ya fueron procesadas."
            );

            return;
        }

        try {

            console.log(
                "Procesando notas de reparación..."
            );

            const respuesta = await fetch(
                "/notas_academicas/calc_prom_est/",
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken":
                            obtener_csrf_token(),

                        "Content-Type":
                            "application/json"
                    }
                }
            );

            const resultado =
                await respuesta.json();

            console.log(
                "Resultado reparación:",
                resultado
            );

            if (
                respuesta.ok &&
                resultado.estado === "exito"
            ) {

                localStorage.setItem(
                    CLAVE_REPARACIONES,
                    "true"
                );

                console.log(
                    "Las notas de reparación fueron procesadas correctamente."
                );
            }

        } catch (error) {

            console.error(
                "Error al procesar reparaciones:",
                error
            );
        }
    }


    // ==========================================================
    // ACTUALIZAR TRAYECTOS
    // ==========================================================

    async function ejecutar_actualizacion_trayectos() {

        if (
            localStorage.getItem(
                CLAVE_TRAYECTOS
            ) === "true"
        ) {

            console.log(
                "Los trayectos ya fueron actualizados."
            );

            return;
        }


        // ------------------------------------------------------
        // LAS REPARACIONES DEBEN HABER TERMINADO
        // ------------------------------------------------------

        if (
            localStorage.getItem(
                CLAVE_REPARACIONES
            ) !== "true"
        ) {

            console.log(
                "Las reparaciones todavía no han sido procesadas."
            );

            return;
        }


        try {

            console.log(
                "Actualizando trayectos..."
            );

            const respuesta = await fetch(
                "/notas_academicas/act_tray_est/",
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken":
                            obtener_csrf_token(),

                        "Content-Type":
                            "application/json"
                    }
                }
            );

            const resultado =
                await respuesta.json();

            console.log(
                "Resultado trayectos:",
                resultado
            );

            if (
                respuesta.ok &&
                resultado.estado === "exito"
            ) {

                localStorage.setItem(
                    CLAVE_TRAYECTOS,
                    "true"
                );

                console.log(
                    "Trayectos actualizados correctamente."
                );
            }

        } catch (error) {

            console.error(
                "Error al actualizar trayectos:",
                error
            );
        }
    }


    // ==========================================================
    // COMPROBAR FECHA Y HORA
    // ==========================================================

    function comprobar_fecha_ejecucion() {

        const ahora = new Date();


        // ======================================================
        // REPARACIONES
        // ======================================================

        if (
            ahora.getTime() >=
            FECHA_REPARACIONES.getTime()
        ) {

            ejecutar_reparaciones();
        }


        // ======================================================
        // ACTUALIZACIÓN DE TRAYECTOS
        // ======================================================

        if (
            ahora.getTime() >=
            FECHA_ACTUALIZACION_TRAYECTOS.getTime()
        ) {

            ejecutar_actualizacion_trayectos();
        }


        // ======================================================
        // VERIFICAR FINALIZACIÓN
        // ======================================================

        const reparaciones_realizadas =
            localStorage.getItem(
                CLAVE_REPARACIONES
            ) === "true";

        const trayectos_realizados =
            localStorage.getItem(
                CLAVE_TRAYECTOS
            ) === "true";


        if (
            reparaciones_realizadas &&
            trayectos_realizados
        ) {

            clearInterval(intervalo);

            console.log(
                "Proceso académico 2027 finalizado."
            );
        }
    }


    // ==========================================================
    // COMPROBAR CADA SEGUNDO
    // ==========================================================

    const intervalo = setInterval(
        comprobar_fecha_ejecucion,
        1000
    );


    // ==========================================================
    // COMPROBAR AL CARGAR LA PÁGINA
    // ==========================================================

    comprobar_fecha_ejecucion();

});