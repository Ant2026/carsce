document.addEventListener("DOMContentLoaded", () => {
   
    const formulario_verificar = document.getElementById("formulario_comprar_usuario");
    const btn_reenviar_codigo = document.getElementById("btn_reenviar_codigo");
    const contador_reenvio = document.getElementById("contador_reenvio");
    const contador_codigo = document.getElementById("contador_codigo");

    const input_password = document.getElementById("password");

    const dialogo_correos = document.getElementById("dialogo_correos");

    const formulario_enviar = document.getElementById("formulario_enviar");

    const label_correo_principal = document.getElementById("label_correo_principal");
    const label_correo_secundario = document.getElementById("label_correo_secundario");

    const input_radios_correo_principal = document.getElementById("correo_principal");
    const input_radios_correo_secundario = document.getElementById("correo_secundario");

    let fechaExpiracion = Number(contador_codigo.dataset.expiracion);
    let intervaloCodigo = null;
    let intervaloReenvio = null;
    let esReenvio = false;

    input_password.addEventListener("input", () => {
        input_password.value = input_password.value
            .toUpperCase()
            .replace(/[^A-Z0-9]/g, "");
    });

    function iniciarContadorCodigo(expiracion) {
        // Convertir la fecha ISO a timestamp en segundos
        fechaExpiracion = Math.floor(new Date(expiracion).getTime() / 1000);

        clearInterval(intervaloCodigo);

        function actualizar() {
            const ahora = Math.floor(Date.now() / 1000);
            const restante = fechaExpiracion - ahora;

            if (restante <= 0) {
                contador_codigo.textContent = "Expirado";

                // Habilitar el botón Reenviar código
                btn_reenviar_codigo.disabled = false;
                contador_reenvio.textContent = "0";

                clearInterval(intervaloCodigo);
                clearInterval(intervaloReenvio);
                return;
            }

            const minutos = Math.floor(restante / 60);
            const segundos = restante % 60;

            contador_codigo.textContent =
                `${String(minutos).padStart(2, "0")}:${String(segundos).padStart(2, "0")}`;
        }

        actualizar();
        intervaloCodigo = setInterval(actualizar, 1000);
    }

    function iniciarContadorReenvio(expiracion) {
        // Convertir la fecha ISO a timestamp en segundos
        const fechaExpiracion = Math.floor(new Date(expiracion).getTime() / 1000);

        btn_reenviar_codigo.disabled = true;

        clearInterval(intervaloReenvio);

        function actualizar() {
            const ahora = Math.floor(Date.now() / 1000);
            const restante = fechaExpiracion - ahora;

            if (restante <= 0) {
                clearInterval(intervaloReenvio);

                btn_reenviar_codigo.disabled = false;
                contador_reenvio.textContent = "0";

                return;
            }

            contador_reenvio.textContent = restante;
        }

        actualizar();
        intervaloReenvio = setInterval(actualizar, 1000);
    }

    async function exite_codigo() {
        try {
            const respuesta = await fetch("/exist_cod/");
            const resultado = await respuesta.json();
            console.log(resultado);

           if (resultado.estado === "exito" || resultado.estado === "codigo_enviado") {
                iniciarContadorCodigo(resultado.fecha_expiracion);
            }

            if (resultado.estado === "expirado") {
                btn_reenviar_codigo.disabled = false;
                contador_reenvio.textContent = "0";

                await Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                return;
            }

            if (resultado.estado === "no_exite") {
                await Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                esReenvio = false;
                correos_electronicos();
            }
        } catch (error) {
            console.error(error);
        }
    }
    exite_codigo();

    async function correos_electronicos() {
        try {
            const respuesta = await fetch("/corr_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            label_correo_principal.textContent = resultado.correos.correo_principal;
            input_radios_correo_principal.value = resultado.correos.correo_principal;

            if (resultado.correos.correo_secundario) {
                label_correo_secundario.textContent = resultado.correos.correo_secundario;
                input_radios_correo_secundario.value = resultado.correos.correo_secundario;

            } else {
                label_correo_secundario.textContent = "";
                input_radios_correo_secundario.value = "";
                input_radios_correo_secundario.checked = false;
            }

            dialogo_correos.showModal();
        } catch (error) {
            console.error(error);
        }
    }

    btn_reenviar_codigo.addEventListener("click", async () => {
        esReenvio = true;
        await correos_electronicos();
    });

    formulario_enviar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            Swal.fire({
                title: "Enviando código...",
                html: "Espere un momento por favor.",
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => Swal.showLoading()
            });

            const formulario = new FormData(formulario_enviar);

            const url = esReenvio ? "/reenv_cod_btn/" : "/env_cod_usr/";

            const respuesta = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            dialogo_correos.close();
            Swal.close();

            await Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon
            });

            if (resultado.estado === "exito" || resultado.estado === "codigo_enviado") {
                iniciarContadorCodigo(resultado.fecha_expiracion);
                window.location.href = "/panel_rec_cred/";
            }

            esReenvio = false; // Restablece el estado
        } catch (error) {
            Swal.close();
            console.error(error);
        }
    });

});