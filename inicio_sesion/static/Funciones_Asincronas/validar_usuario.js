document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_comprar_usuario");
    const contador_codigo = document.getElementById("contador_codigo");

    if (!contador_codigo) return;
    
    let fechaExpiracion = parseInt(contador_codigo.dataset.expiracion);

    function actualizarTiempo() {
        const ahora = Math.floor(Date.now() / 1000);
        const restante = fechaExpiracion - ahora;

        if (restante <= 0) {
            contador_codigo.textContent = "Expirado";
            return false;
        }

        const minutos = Math.floor(restante / 60);
        const segundos = restante % 60;

        contador_codigo.textContent = `${minutos}:${segundos.toString().padStart(2, "0")}`;

        return true;
    }
    actualizarTiempo();

    const intervalo = setInterval(() => {
        if (!actualizarTiempo()) {
            clearInterval(intervalo);
        }
    }, 1000);
    
    formulario.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const datos_formulario = new FormData(formulario);
            const respuesta = await fetch("/comprobar_usuario/", {
                method: "POST",
                body: datos_formulario,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });
            const resultado = await respuesta.json();

            if (resultado.estado === "exito") {
                window.location.href = "/panel_recuperar_credenciales/";
            } else {
                await Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

                formulario.reset();
            }
        } catch (error) {
            Swal.fire({
                title: "Error",
                text: error.message,
                icon: "error",
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        }
    });
});