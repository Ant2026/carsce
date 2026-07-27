document.addEventListener("DOMContentLoaded", () => {
    const nombres_registrado = document.getElementById("nombres_usuario");
    const apellidos_registrado = document.getElementById("apellidos_usuario");
    const cedula_identidad_registrado = document.getElementById("CI");

    const telefono_principal_registrado = document.getElementById("telefono_principal_usuario");
    const correo_principal_registrado = document.getElementById("correo_principal_usuario");

    const formulario_personal = document.getElementById("formulario_CRP");

    const input_correo_electronico = document.getElementById("Correo");
    const select_dominio_correo = document.getElementById("dominio");
    const mensaje_correo_electronico = document.getElementById("mensaje_correo_electronico");
    const btn_registro = document.getElementById("btn_registro");

    async function datos_registrado() {
        try {
            const respuesta = await fetch("/datos_registrado/")
            const resultado = await respuesta.json()
            console.log(resultado);

            if (resultado.estado == "no_exite") {
                await Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                
                window.location.href = resultado.url;
            }

            nombres_registrado.value = resultado.usuario.nombres
            apellidos_registrado.value = resultado.usuario.apellidos
            cedula_identidad_registrado.value = resultado.usuario.cedula_identidad
            
            telefono_principal_registrado.value = resultado.contacto.telefono_personal
            correo_principal_registrado.value = resultado.contacto.correo_electronico
        } catch (error) {
            console.error(error)
        }
    }
    datos_registrado()


    async function validarCorreo(inputCorreo, selectDominio, mensaje) {
        const correo = inputCorreo.value.trim();
        const dominio = selectDominio.value;

        console.log(correo);
        if (correo === "" || dominio === "") {
            inputCorreo.setCustomValidity("");
            inputCorreo.classList.remove("is-valid", "is-invalid");
            mensaje.innerHTML = "";
            return;
        }

        if (dominio === "" || correo.length < 5 || correo.length > 30) {
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


    formulario_personal.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_personal);

            const respuesta = await fetch("/completar_registro_personal/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                title: resultado.titulo,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado === "exito") {
                window.location.href = resultado.url;
            }
        } catch (error) {
            console.error(error)
        }
    });
});