document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_contrasenia");

    formulario.addEventListener("submit", async function(e) {
        e.preventDefault();

        const datos_formulario = new FormData(formulario);

        try {
            const respuesta = await fetch("", {
                method: "POST",
                body: datos_formulario
            });
            const resultado = await respuesta.json();

            if (resultado.estado === "exito") {
                await Swal.fire({
                    text: "Contraseña actualizada exitosamente",
                    icon: "success",
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

                window.location.href = "/buscar_usuario/";
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