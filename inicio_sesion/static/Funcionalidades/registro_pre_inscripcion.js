document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario")

    formulario.addEventListener("submit", async function(e) {
        e.preventDefault()

        const datos_formulario = new FormData(formulario)

        try {
            const respuesta = await fetch("", {
                method: "POST",
                body: datos_formulario
            });
            const resultado = await respuesta.json()

            if (resultado.estado == "exito") {
                Swal.fire({
                    title: "Exito",
                    text: resultado.descripcion,
                    icon: "success",
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            } else {
                Swal.fire({
                    title: "Error",
                    text: resultado.descripcion,
                    icon: "error",
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }

            formulario.reset()
        } catch (error) {
            console.error(error)
        }
    });

});