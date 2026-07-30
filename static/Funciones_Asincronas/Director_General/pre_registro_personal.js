document.addEventListener("DOMContentLoaded", () => {
    const formulario_registrar = document.getElementById("formulario_registrar");

    const input_cedula_identidad = document.getElementById("cedula_identidad");
    const select_nacionalidad = document.getElementById("nacionalidad");
    const small_mensaje_cedula_identidad = document.getElementById("mensaje_cedula_identidad");

    const btn_registro = document.getElementById("btn_registro");
  
    async function validarCedula(selectNacionalidad, inputCedula, mensaje) {
        const nacionalidad = selectNacionalidad.value;
        const cedula = inputCedula.value.trim();

        if (cedula.length === 0) {
            mensaje.textContent = "";
            inputCedula.setCustomValidity("");
            inputCedula.classList.remove("is-valid", "is-invalid");
            btn_registro.disabled = false;
            return;
        }

        const valida = (nacionalidad === "V" && cedula.length >= 7 && cedula.length <= 8) || (nacionalidad === "E" && cedula.length >= 8 && cedula.length <= 10);
        if (!valida) return;

        try {
            const formulario = new FormData();
            formulario.append("nacionalidad", nacionalidad);
            formulario.append("cedula", cedula);

            const respuesta = await fetch("/verificar_cedula_representante/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });

            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.existe) {
                inputCedula.setCustomValidity(
                    "Ya se encuentra un usuario registrado con esta cédula de identidad."
                );

                inputCedula.classList.add("is-invalid");
                inputCedula.classList.remove("is-valid");

                mensaje.textContent = "Ya se encuentra un usuario registrado con esta cédula de identidad.";
                mensaje.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                inputCedula.setCustomValidity("");

                inputCedula.classList.remove("is-invalid");
                inputCedula.classList.add("is-valid");

                mensaje.textContent = "La cédula de identidad está disponible.";
                mensaje.style.color = "#198754";

                btn_registro.disabled = false;
            }

        } catch (error) {
            console.error(error);
        }
    }

    select_nacionalidad.addEventListener("change", async () => {
        validarCedula(select_nacionalidad, input_cedula_identidad, small_mensaje_cedula_identidad);
    });

    input_cedula_identidad.addEventListener("input", async () => {
        validarCedula(select_nacionalidad, input_cedula_identidad, small_mensaje_cedula_identidad);
    });


    formulario_registrar.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/pre_registro_personal/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
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