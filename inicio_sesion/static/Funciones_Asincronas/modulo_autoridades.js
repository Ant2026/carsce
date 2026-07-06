document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registrar_autoridades")
    const formulario_actualizar = document.getElementById("formulario_actualizar_autoridades")

    const contenedor_autoridades = document.getElementById("contenedor_autoridades")

    const input_autoridad_oculto = document.getElementById("usuario_seleccionado")
    const input_nombres_actualizar = document.getElementById("nombres_actualizar_autoridades")
    const input_apellidos_actualizar = document.getElementById("apellidos_actualizar_autoridades")
    const select_genero_actualizar = document.getElementById("genero_actualizar_autoridades")
    const select_cargo_actualizar = document.getElementById("cargo_actualizar_autoridades")
    const input_resolucion_actualizar = document.getElementById("resolucion_actualizar_autoridades")

    const dialogo_actualizar_autoridad = document.getElementById("dialogo_actualizar_autoridades")
    const btn_cerrar = document.getElementById("cerrar_dialogo")

    const input_cedula_actualizar = document.getElementById("cedula_actualizar_autoridades");
    const select_nacionalidad_actualizar = document.getElementById("nacionalidad_actualizar_autoridades");

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

    async function obtener_autoridades() {
        try {
            const respuesta = await fetch("/autoridades_registradas/")
            const resultado = await respuesta.json()
            console.log(resultado)

            contenedor_autoridades.innerHTML = "";

            resultado.forEach(autoridad => {
                contenedor_autoridades.innerHTML += `
                    <tr data-id=${autoridad.id_autoridad}>
                        <td>${autoridad.nombres}</td>
                        <td>${autoridad.apellidos}</td>
                        <td>${autoridad.cedula_identidad}</td>
                        <td>${autoridad.cargo}</td>
                        <td>${autoridad.resolucion}</td>
                    </tr>
                `;
            });

        } catch (error) {
            console.error(error)
        }
    }
    obtener_autoridades();

    formulario_registrar.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)

            const respuesta = await fetch("/modulo_autoridades/", {
                method: "POST",
                body: formulario
            });
             const resultado = await respuesta.json()
            console.log(resultado)

            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

                await obtener_autoridades()
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

    contenedor_autoridades.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr")
        if (!fila) return

        try {
            const formulario = new FormData()
            formulario.append("id", fila.dataset.id)

            const respuesta = await fetch("/datos_autoridad/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()
            console.log(resultado)

            input_autoridad_oculto.value = resultado.id_autoridad
            input_nombres_actualizar.value = resultado.nombres
            input_apellidos_actualizar.value = resultado.apellidos
            
            const [nacionalidad, cedula] = resultado.cedula.split("-");

            const option_nacionalidad = document.createElement("option")
            option_nacionalidad.value = nacionalidad
            option_nacionalidad.textContent = nacionalidad
            option_nacionalidad.selected = true
            option_nacionalidad.hidden = true
            select_nacionalidad_actualizar.append(option_nacionalidad)
            
            input_cedula_actualizar.value = cedula
        
            const option_genero = document.createElement("option")
            option_genero.value = resultado.genero
            option_genero.textContent = resultado.genero
            option_genero.selected = true
            option_genero.hidden = true
            select_genero_actualizar.append(option_genero)

            const option_cargo = document.createElement("option")
            option_cargo.value = resultado.cargo
            option_cargo.textContent = resultado.cargo
            option_cargo.selected = true
            select_cargo_actualizar.append(option_cargo)

            input_resolucion_actualizar.value = resultado.resolucion

            dialogo_actualizar_autoridad.showModal();
        } catch (error) {
            console.error(error)
        }
    });

    btn_cerrar.addEventListener("click", () => {
        dialogo_actualizar_autoridad.close();
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar)

            const respuesta = await fetch("/actualizar_datos_autoridad/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json()
            
            dialogo_actualizar_autoridad.close();
            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

                await obtener_autoridades()
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
        } catch (error) {
            console.error(error)
        }
    });

    function longitud_identidad() {
        const nacionalidad = select_nacionalidad_actualizar.value;

        input_cedula_actualizar.removeAttribute("minLength");
        input_cedula_actualizar.removeAttribute("maxLength");

        switch (nacionalidad) {
            case "V":
                input_cedula_actualizar.disabled = false;
                input_cedula_actualizar.maxLength = 8;
                input_cedula_actualizar.minLength = 7;
                input_cedula_actualizar.placeholder = "Cédula de Identidad (7-8)";
                break;
            case "E":
                input_cedula_actualizar.disabled = false;
                input_cedula_actualizar.maxLength = 10;
                input_cedula_actualizar.minLength = 8;
                input_cedula_actualizar.placeholder = "Pasaporte/DNI (8-10)";
                break;
        }
    }
    longitud_identidad();

    input_cedula_actualizar.addEventListener("input", function () {
        this.value = this.value.replace(/\D/g, "");
    });

    select_nacionalidad_actualizar.addEventListener("change", longitud_identidad);

}); 