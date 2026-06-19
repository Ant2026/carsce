document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_login");

    formulario.addEventListener("submit", async function(e) {
        e.preventDefault();

        const datos_formulario = new FormData(formulario);
        try {
            const respuesta = await fetch("/inicio_sesion/", {
                method: "POST",
                body: datos_formulario
            });
            const resultado = await respuesta.json();
            if (resultado.success) {
                window.location.href = resultado.url;
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