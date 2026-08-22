document.addEventListener("DOMContentLoaded", () => {
    const formulario_registrar = document.getElementById("formulario_registrar");

    const input_cedula_identidad = document.getElementById("cedula_identidad");
    const select_nacionalidad = document.getElementById("nacionalidad");
    const small_mensaje_cedula_identidad = document.getElementById("mensaje_cedula_identidad");

    const input_correo_electronico = document.getElementById("correo_electronico");
    const select_dominio = document.getElementById("dominio");
    const small_mensaje_correo_electronico = document.getElementById("mensaje_correo_electronico");

    const input_telefono = document.getElementById("numero_telefonico");
    const select_prefijo = document.getElementById("prefijo_telefono");

    const btn_registro = document.getElementById("btn_registro");

    configurarCedula(select_nacionalidad, input_cedula_identidad);
    configurarCorreo(input_correo_electronico, select_dominio);
    configurarTelefono(input_telefono, select_prefijo);

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

        try {
            const formulario = new FormData();
            formulario.append("nacionalidad", nacionalidad);
            formulario.append("cedula", cedula);

            const respuesta = await fetch("/validar_ci_usr/", {
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


    async function validar_correos(correo, dominio, msg) {
        try {
            const formulario = new FormData();
            formulario.append("correo", correo.value);
            formulario.append("dominio", dominio.value);

            const respuesta = await fetch("/validar_email/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.existe) {
                correo.setCustomValidity("Ya existe un usuario con este correo electrónico.");
                correo.classList.add("is-invalid");
                correo.classList.remove("is-valid");

                msg.textContent = "Ya existe un usuario con este correo electrónico.";
                msg.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                correo.setCustomValidity("");
                correo.classList.add("is-valid");
                correo.classList.remove("is-invalid");

                msg.textContent = "El correo electrónico está disponible.";
                msg.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_correo_electronico.addEventListener("input", async () => {
        validar_correos(input_correo_electronico, select_dominio, small_mensaje_correo_electronico);
    });

    select_dominio.addEventListener("change", async () => {
        validar_correos(input_correo_electronico, select_dominio, small_mensaje_correo_electronico);
    });


    formulario_registrar.addEventListener("submit", async function (e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/pre_reg_personal/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
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