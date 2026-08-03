document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registrar");
    const registrar_nombre_aula = document.getElementById("registrar_nombre_aula");
    const mensaje_nombre_aula = document.getElementById("mensaje_nombre_aula");
    const btn_registrar = document.getElementById("btn_registrar");

    async function validar_seccion() {
        try {
            const formulario = new FormData();
            formulario.append("aula", registrar_nombre_aula.value);

            const respuesta = await fetch("/val_aula/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.existe) {
                registrar_nombre_aula.setCustomValidity("Ya existe un pnf con el mismo nombre.");
                registrar_nombre_aula.classList.add("is-invalid");
                registrar_nombre_aula.classList.remove("is-valid");

                mensaje_nombre_aula.textContent = "Ya existe un pnf con el mismo nombre.";
                mensaje_nombre_aula.style.color = "#dc3545";

                btn_registrar.disabled = true;
            } else {
                registrar_nombre_aula.setCustomValidity("");
                registrar_nombre_aula.classList.add("is-valid");
                registrar_nombre_aula.classList.remove("is-invalid");

                mensaje_nombre_aula.textContent = "El nombre del PNF está disponible.";
                mensaje_nombre_aula.style.color = "#198754";

                btn_registrar.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    registrar_nombre_aula.addEventListener("input", async () => {
        registrar_nombre_aula.value = registrar_nombre_aula.value.replace(
            /[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s_-]/g,
            ""
        );

        await validar_seccion();
    });

    registrar_nombre_aula.addEventListener("paste", async () => {
        setTimeout(async () => {
            registrar_nombre_aula.value = registrar_nombre_aula.value.replace(
                /[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s_-]/g,
                ""
            );

            await validar_seccion();
        }, 0);
    });
    
    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)

            const respuesta = await fetch("/reg_aula/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json()
            console.log(resultado)

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
         
            if (resultado.estado == "exito") {
                formulario_registrar.reset()
            }
        } catch (error) {
            console.error(error);
        }
    });
});