document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_pre_inscripcion")

    formulario.addEventListener("submit", async function(e) {
        e.preventDefault()
        try {
            const datos_formulario = new FormData(formulario)
            const respuesta = await fetch("", {
                method: "POST",
                body: datos_formulario
            });
            const resultado = await respuesta.json()
            console.log(resultado)

            Swal.fire({
                icon: resultado.icon,
                text: resultado.descripcion,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            formulario.reset()
        } catch (error) {
            console.error(error)
        }
    });

});