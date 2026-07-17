document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_buscar_usuario");

    formulario.addEventListener("submit", async function(e) {
        e.preventDefault()
        const datos_formulario = new FormData(formulario)

        try {
            const respuesta = await fetch("", {
                method: "POST",
                body: datos_formulario
            });
            const resultado = await respuesta.json()
            
            if (resultado.estado === "exito") {
                window.location.href = "/../../Sesion/comprobar_usuario/";
            } else {
                Swal.fire({
                    title: "Error",
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                formulario.reset()
            }
        } catch (error) {
            console.error(error);
        }
    });
});