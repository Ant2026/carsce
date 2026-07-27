document.addEventListener("DOMContentLoaded", () => {
    const formulario_buscar = document.getElementById("formulario_buscar_usuario");

    formulario_buscar.addEventListener("submit", async function(e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_buscar);

            const respuesta = await fetch("/buscar_usuario/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.estado === "exito") {
                window.location.href = "/comprobar_usuario/";
            } else {
                Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }

            formulario_buscar.reset()
        } catch (error) {
            console.error(error);
        }
    });
});