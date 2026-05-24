document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_pre_inscripcion")

    formulario.addEventListener("submit", async function(e) {
        e.preventDefault()

        const datos_formulario = new FormData(formulario)

        try {
            const respuesta = await fetch("", {
                method: "POST",
                body: datos_formulario
            });
            const resultado = await respuesta.json()

                Swal.fire({
                    title: resultado.icon,
                    text: resultado.descripcion,
                    icon: "success",
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

            formulario.reset()
        } catch (error) {
            console.error(error)
        }
    });

});