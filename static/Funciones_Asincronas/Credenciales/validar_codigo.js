document.addEventListener("DOMContentLoaded", () => {
   
    const formulario_verificar = document.getElementById("formulario_comprar_usuario");
    const btn_reenviar_codigo = document.getElementById("btn_reenviar_codigo");
    const contador_reenvio = document.getElementById("contador_reenvio");
    const contador_codigo = document.getElementById("contador_codigo");

    let fechaExpiracion = Number(contador_codigo.dataset.expiracion);

    let intervaloCodigo = null;
    let intervaloReenvio = null;

    // Contador de vigencia del código enviado
    function iniciarContadorCodigo(expiracion) {
        fechaExpiracion = expiracion;

        clearInterval(intervaloCodigo);
        function actualizar() {
            const ahora = Math.floor(Date.now() / 1000);

            const restante = fechaExpiracion - ahora;
            if (restante <= 0) {
                contador_codigo.textContent = "Expirado";
                clearInterval(intervaloCodigo);
                return;
            }
            const minutos = Math.floor(restante / 60);
            const segundos = restante % 60;

            contador_codigo.textContent = `${String(minutos).padStart(2,"0")}:${String(segundos).padStart(2,"0")}`;
        }
        actualizar();

        intervaloCodigo = setInterval(actualizar, 1000);
    }
    
    function ejecutarContadorReenvio(fin) {
        btn_reenviar_codigo.disabled = true;

        clearInterval(intervaloReenvio);

        function actualizar() {

            const restante = Math.ceil((fin - Date.now()) / 1000);

            if (restante <= 0) {
                clearInterval(intervaloReenvio);
                btn_reenviar_codigo.disabled = false;
                contador_reenvio.textContent = "0";
                localStorage.removeItem("finReenvio");
                return;
            }

            contador_reenvio.textContent = restante;
        }

        actualizar(); // <-- Muy importante

        intervaloReenvio = setInterval(actualizar, 1000);
    }

    function iniciarContadorReenvio() {
        const fin = Date.now() + 60000;
        localStorage.setItem("finReenvio", fin);

        ejecutarContadorReenvio(fin);
    }
    iniciarContadorReenvio();
   
    const fin = localStorage.getItem("finReenvio");

    if (fin) {
        ejecutarContadorReenvio(Number(fin));
    }

    async function enviar_codigo() {
        try {
            Swal.fire({
                title: "Enviando código...",
                html: "Espere un momento por favor.",
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            const respuesta = await fetch("/enviar_codigo_usuario/");
            const resultado = await respuesta.json();

            Swal.close();
            await Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado === "exito") {
                iniciarContadorCodigo(resultado.fecha_expiracion);
            }
        } catch (error) {
            Swal.close();
            console.error(error);
        }
    }
    enviar_codigo();

    formulario_verificar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_verificar);
            
            const respuesta = await fetch("/comprobar_codigo_usuario/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
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
                window.location.href = "/panel_recuperar_credenciales/";
            }
            formulario_verificar.reset();
        } catch (error) {
            console.error(error);
        }
    });

    btn_reenviar_codigo.addEventListener("click", async () => {
        try {
            btn_reenviar_codigo.disabled = true;

            const respuesta = await fetch("/reenviar_codigo_btn/");
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado === "exito") {
                await enviar_codigo();
                iniciarContadorReenvio();
            } else if (resultado.estado === "reenviar") {
                window.location.href = resultado.url;
            } else {
                btn_reenviar_codigo.disabled = false;
            }
        } catch (error) {
            console.error(error);
            btn_reenviar_codigo.disabled = false;
        }
    });
});