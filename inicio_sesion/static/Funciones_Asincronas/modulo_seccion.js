document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("registrarsecciones")
    const input_registrar_seccion = document.getElementById("registrar_seccion")

    const contenedor_secciones = document.getElementById("tabla_secciones")

    const dialogo_actualizar = document.getElementById("dialogo_actualizar_secciones")
    const btn_cerrar = document.getElementById("cerrar_dialogo")
    const formulario_actualizar = document.getElementById("modificarnsecciones")
    const input_seccion_oculto = document.getElementById("secciones_seleccionado")
    const input_actualizar_seccion = document.getElementById("actualizar_seccion")
  
    function getCookie(nombre) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(nombre + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(nombre.length + 1)
                    );
                    break;
                }
            }
        }

        return cookieValue;
    }
    const csrftoken = getCookie("csrftoken");

    async function cargar() {
        try {
            const respuesta = await fetch("/secciones_registradas/");
            const resultado = await respuesta.json();

            contenedor_secciones.innerHTML = "";

            let filas = "";

            resultado.secciones.forEach((seccion, index) => {
                filas += `
                    <tr data-id-seccion="${seccion.id_seccion}">
                        <td>${index + 1}</td>
                        <td>${seccion.seccion}</td>
                    </tr>
                `;
            });

            contenedor_secciones.innerHTML = `
                <table class="tabla_nucleo">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Sección</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filas}
                    </tbody>
                </table>
            `;

        } catch (error) {
            console.error(error);
        }
    }
    cargar();

    contenedor_secciones.addEventListener("click", async function (e) {
        const fila = e.target.closest("tr");
        if (!fila || !fila.dataset.idSeccion) return;

        try {

            const formulario = new FormData();
            formulario.append("seccion", fila.dataset.idSeccion);

            const respuesta = await fetch("/datos_seccion/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            input_seccion_oculto.value = resultado.seccion.id_seccion;

            input_actualizar_seccion.value = resultado.seccion.seccion;

            dialogo_actualizar.showModal();
        } catch (error) {
            console.error(error);
        }
    });

    btn_cerrar.addEventListener("click", () => {
        dialogo_actualizar.close();
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar)

            const respuesta = await fetch("/guardar_actualizacion_seccion/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()

            dialogo_actualizar.close();
            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_actualizar.reset()
        } catch (error) {
            console.error(error)
        }
    });

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)

            const respuesta = await fetch("/modulo_seccion/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()

            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_registrar.reset()
        } catch (error) {
            console.error(error)
        }
    });
});