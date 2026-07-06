document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_pre_registro_personal");

    formulario.addEventListener("submit", async function(e) {
        e.preventDefault();

        const datos_formulario = new FormData(formulario);
        try {
            const respuesta = await fetch("/pre_registro_personal/", {
                method: "POST",
                body: datos_formulario
            });
            const resultado = await respuesta.json();
            if (resultado.success) {
                Swal.fire({
                    title: resultado.icon,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            } else {
                Swal.fire({
                    title: resultado.icon,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                formulario.reset();
            }
        } catch (error) {
            console.error(error);
        }
    });

});