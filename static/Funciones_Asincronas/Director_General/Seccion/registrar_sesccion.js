document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registrar");

    const select_registrar_turno = document.getElementById("registro_turno");
    const input_registrar_seccion = document.getElementById("registro_seccion");
    const mensaje_nombre_seccion = document.getElementById("mensaje_nombre_seccion");

    const btn_registrar = document.getElementById("btn_registro");

    async function validar_seccion() {
        try {
            const formulario = new FormData();
            formulario.append("seccion", input_registrar_seccion.value);

            const respuesta = await fetch("/val_sec/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.existe) {
                input_registrar_seccion.setCustomValidity("Ya existe una sección con el mismo nombre.");
                input_registrar_seccion.classList.add("is-invalid");
                input_registrar_seccion.classList.remove("is-valid");

                mensaje_nombre_seccion.textContent = "Ya existe una sección con el mismo nombre.";
                mensaje_nombre_seccion.style.color = "#dc3545";

                btn_registrar.disabled = true;
            } else {
                input_registrar_seccion.setCustomValidity("");
                input_registrar_seccion.classList.add("is-valid");
                input_registrar_seccion.classList.remove("is-invalid");

                mensaje_nombre_seccion.textContent = "El nombre de la sección está disponible.";
                mensaje_nombre_seccion.style.color = "#198754";

                btn_registrar.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }
    input_registrar_seccion.addEventListener("input", validar_seccion);

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/reg_sec/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_registrar.reset();
            }
        } catch (error) {
            console.error(error);
        }
    }); 

});