document.addEventListener("DOMContentLoaded", () => {
    const formulario_documento = document.getElementById("formulario_documento_estudiante");

    formulario_documento.addEventListener("submit", async (e) => {
        e.preventDefault();

        try {
            const respuesta = await fetch("/registro_documento/", {
                method: "POST",
                body: new FormData(formulario_documento)
            });

            const resultado = await respuesta.json();

            if (resultado.estado == "success") {
                Swal.fire({
                    title: "Éxito",
                    text: "Los datos se registraron exitosamente",
                    icon: "success",
                    allowOutsideClick: false,
                    allowEscapeKey: false
                }).then(() => {
                    window.location.href = "/panel_usuario/";
                });
            } else {
                Swal.fire({
                    title: resultado.titulo || "Error",
                    text: resultado.descripcion,
                    icon: resultado.icon || "error",
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }

            formulario_documento.reset(); 
        } catch (error) {
            console.error(error);
        }
    });
});