document.addEventListener("DOMContentLoaded", () => {
    const formulario_registro = document.getElementById("formulario_registro");

    const select_nacionalidad = document.getElementById("nacionalidad");
    const input_cedula_identidad = document.getElementById("cedula_identidad");
    const mensaje_cedula_identidad = document.getElementById("mensaje_cedula_identidad");

    const input_correo_electronico = document.getElementById("correo_electronico");
    const select_dominio_correo = document.getElementById("dominio");
    const mensaje_correo_electronico = document.getElementById("mensaje_correo_electronico");

    const prefijo_telefono = document.getElementById("prefijo_telefono");
    const numero_telefonico = document.getElementById("numero_telefonico");

    const input_nombre_usuario = document.getElementById("nombre_usuario");
    const mensaje_nombre_usuario = document.getElementById("mensaje_nombre_usuario");
    
    const input_password = document.getElementById("password");
    const mensaje_password = document.getElementById("mensaje_password");

    const btn_registro = document.getElementById("btn_registro");

    configurarCedula(select_nacionalidad, input_cedula_identidad);
    configurarCorreo(input_correo_electronico, select_dominio_correo);
    configurarTelefono(numero_telefonico, prefijo_telefono);

    async function buscar_usuario(nacionalidad, cedula) {
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

            if (resultado.existe == true) {
                input_cedula_identidad.setCustomValidity("Ya se encuentra un usuario registrado con esta cédula de identidad.");

                input_cedula_identidad.classList.add("is-invalid");
                input_cedula_identidad.classList.remove("is-valid");

                mensaje_cedula_identidad.textContent = "Ya se encuentra un usuario registrado con esta cédula de identidad.";
                mensaje_cedula_identidad.style.color = "#dc3545";

                btn_registro.disabled = true;
            }

            if (resultado.existe == false) {
                input_cedula_identidad.setCustomValidity("");

                input_cedula_identidad.classList.remove("is-invalid");
                input_cedula_identidad.classList.add("is-valid");

                mensaje_cedula_identidad.textContent = "La cédula de identidad está disponible.";
                mensaje_cedula_identidad.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }
    
    select_nacionalidad.addEventListener("change", () => {
        if (!select_nacionalidad.value || !input_cedula_identidad.value.trim()) {
            mensaje_cedula_identidad.textContent = "";
            return;
        }

        buscar_usuario(select_nacionalidad.value, input_cedula_identidad.value);
    });

    input_cedula_identidad.addEventListener("input", () => {
        if (!select_nacionalidad.value || !input_cedula_identidad.value.trim()) {
            mensaje_cedula_identidad.textContent = "";
            return;
        }

        buscar_usuario(select_nacionalidad.value, input_cedula_identidad.value);
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

    input_correo_electronico.addEventListener("input", () => {
        if (!input_correo_electronico.value.trim() || !select_dominio_correo.value) {
            mensaje_correo_electronico.textContent = "";
            return;
        }

        validar_correos(input_correo_electronico, select_dominio_correo, mensaje_correo_electronico);
    });

    select_dominio_correo.addEventListener("change", () => {
        if (!input_correo_electronico.value.trim() || !select_dominio_correo.value) {
            mensaje_correo_electronico.textContent = "";
            return;
        }

        validar_correos(input_correo_electronico, select_dominio_correo, mensaje_correo_electronico);
    });
    
    async function buscar_nombre_usuario(nombre_usuario) {
        try {
            const formulario = new FormData();
            formulario.append("nombre_usuario", nombre_usuario);

            const respuesta = await fetch("/val_usuario/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.existe == true) {
                input_nombre_usuario.setCustomValidity("Ya se encuentra un usuario registrado con este nombre de usuario.");

                input_nombre_usuario.classList.add("is-invalid");
                input_nombre_usuario.classList.remove("is-valid");

                mensaje_nombre_usuario.textContent = "Ya se encuentra un usuario registrado con este nombre de usuario.";
                mensaje_nombre_usuario.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                input_nombre_usuario.setCustomValidity("");

                input_nombre_usuario.classList.remove("is-invalid");
                input_nombre_usuario.classList.add("is-valid");

                mensaje_nombre_usuario.textContent = "El nombre de usuario está disponible.";
                mensaje_nombre_usuario.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_nombre_usuario.addEventListener("input", () => {
        if (!input_nombre_usuario.value.trim()) {
            mensaje_nombre_usuario.textContent = "";
            return;
        }

        buscar_nombre_usuario(input_nombre_usuario.value);
    });

    async function buscar_password(password) {
        try {
            const formulario = new FormData();
            formulario.append("password", password);

            const respuesta = await fetch("/val_password/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.existe == true) {
                input_password.setCustomValidity("Ya se encuentra un usuario registrado con esta contraseña.");

                input_password.classList.add("is-invalid");
                input_password.classList.remove("is-valid");

                mensaje_password.textContent = "Ya se encuentra un usuario registrado con esta contraseña.";
                mensaje_password.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                input_password.setCustomValidity("");

                input_password.classList.remove("is-invalid");
                input_password.classList.add("is-valid");

                mensaje_password.textContent = "La contraseña está disponible.";
                mensaje_password.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_password.addEventListener("input", () => {
        if (!input_password.value.trim()) {
            mensaje_password.textContent = "";
            return;
        }

        buscar_password(input_password.value);
    });

    formulario_registro.addEventListener("submit", async function(e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registro);

            const respuesta = await fetch("/registro_est/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                title: resultado.title,
                icon: resultado.icon,
                text: resultado.descripcion,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado === "exito") {
                formulario_registro.reset();
            }
        } catch (error) {
            console.error(error)
        }
    });

});