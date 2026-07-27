document.addEventListener("DOMContentLoaded", () => {
    const formulario_registro = document.getElementById("formulario_registro");

    const select_nacionalidad = document.getElementById("nacionalidad");
    const input_cedula_identidad = document.getElementById("cedula_identidad");
    const mensaje_cedula_identidad = document.getElementById("mensaje_cedula_identidad");

    const input_correo_electronico = document.getElementById("Correo");
    const select_dominio_correo = document.getElementById("dominio");
    const mensaje_correo_electronico = document.getElementById("mensaje_correo_electronico");

    const input_nombre_usuario = document.getElementById("nombre_usuario");
    const mensaje_nombre_usuario = document.getElementById("mensaje_nombre_usuario");
    
    const input_password = document.getElementById("password");
    const mensaje_password = document.getElementById("mensaje_password");

    const btn_registro = document.getElementById("btn_registro");

    async function cedula_identidad() {
        const nacionalidad = select_nacionalidad.value;
        const cedula = input_cedula_identidad.value;
        
        if (cedula.length === 0) {
            mensaje_cedula_identidad.textContent = "";

            input_cedula_identidad.setCustomValidity("");

            input_cedula_identidad.classList.remove("is-valid");
            input_cedula_identidad.classList.remove("is-invalid");
            return;
        }

        if (nacionalidad === "V" && (cedula.length >= 7 && cedula.length <= 8)) {
            await buscar_usuario(nacionalidad, cedula);
        }

        if (nacionalidad === "E" && (cedula.length >= 8 && cedula.length <= 10)) {
            await buscar_usuario(nacionalidad, cedula);
        }
    }
    select_nacionalidad.addEventListener("change", cedula_identidad);
    input_cedula_identidad.addEventListener("input", cedula_identidad);

    async function buscar_usuario(nacionalidad, cedula) {
        try {
            const formulario = new FormData();
            formulario.append("nacionalidad", nacionalidad);
            formulario.append("cedula", cedula);

            const respuesta = await fetch("/verificar_cedula_identidad/", {
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
    
    async function validarCorreo(inputCorreo, selectDominio, mensaje) {
        const correo = inputCorreo.value.trim();
        const dominio = selectDominio.value;

        if (correo === "") {
            inputCorreo.setCustomValidity("");
            inputCorreo.classList.remove("is-valid", "is-invalid");
            mensaje.textContent = "";
            return;
        }

        if (dominio === "" || correo.length < 10 || correo.length > 30) {
            return;
        }

        try {
            const formulario = new FormData();
            formulario.append("correo", correo);
            formulario.append("dominio", dominio);

            const respuesta = await fetch("/verificar_correo_electronico/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            if (resultado.existe) {
                inputCorreo.setCustomValidity("Ya existe un usuario con este correo electrónico.");
                inputCorreo.classList.add("is-invalid");
                inputCorreo.classList.remove("is-valid");

                mensaje.textContent = "Ya existe un usuario con este correo electrónico.";
                mensaje.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                inputCorreo.setCustomValidity("");
                inputCorreo.classList.add("is-valid");
                inputCorreo.classList.remove("is-invalid");

                mensaje.textContent = "El correo electrónico está disponible.";
                mensaje.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_correo_electronico.addEventListener("input", () => {
        validarCorreo(input_correo_electronico, select_dominio_correo, mensaje_correo_electronico);
    });

    select_dominio_correo.addEventListener("change", () => {
        validarCorreo(input_correo_electronico, select_dominio_correo, mensaje_correo_electronico);
    });

    
    async function nombre_usuario() {
        const nombre = input_nombre_usuario.value;
        
        if (nombre.length === 0) {
            mensaje_nombre_usuario.textContent = "";

            input_nombre_usuario.setCustomValidity("");
            input_nombre_usuario.classList.remove("is-valid");
            input_nombre_usuario.classList.remove("is-invalid");
            return;
        }

        if (nombre.length >= 4 && nombre.length <= 10) {
            await buscar_nombre_usuario(nombre);
        }
    }
    input_nombre_usuario.addEventListener("input", nombre_usuario);

    async function buscar_nombre_usuario(nombre_usuario) {
        try {
            const formulario = new FormData();
            formulario.append("nombre_usuario", nombre_usuario);

            const respuesta = await fetch("/verificar_nombre_usuario/", {
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
            }

            if (resultado.existe == false) {
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


    async function contrasenia() {
        const password = input_password.value;

        if (password.length === 0) {
            mensaje_password.textContent = "";

            input_password.setCustomValidity("");
            input_password.classList.remove("is-valid");
            input_password.classList.remove("is-invalid");
            return;
        }

        if (password.length >= 4 && password.length <= 10) {
            await buscar_password(password);
            console.log(password)
        }
    }
    input_password.addEventListener("input", contrasenia);

    async function buscar_password(password) {
        try {
            const formulario = new FormData();
            formulario.append("password", password);

            const respuesta = await fetch("/verificar_password/", {
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
            }

            if (resultado.existe == false) {
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

    formulario_registro.addEventListener("submit", async function(e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registro);

            const respuesta = await fetch("/registro_estudiantil/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            Swal.fire({
                title: resultado.title,
                icon: resultado.icon,
                text: resultado.descripcion,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            formulario_registro.reset();

            mensaje_cedula_identidad.innerHTML = "";
            mensaje_correo_electronico.innerHTML = "";
            mensaje_nombre_usuario.innerHTML = "";
        } catch (error) {
            console.error(error)
        }
    });

});