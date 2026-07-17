document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_login");

    formulario.addEventListener("submit", async function (e) {
        e.preventDefault();

        const datos_formulario = new FormData(formulario);

        Swal.fire({
            title: "Iniciando sesión...",
            html: "Espere un momento por favor.",
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        try {
            const respuesta = await fetch("", {
                method: "POST",
                body: datos_formulario
            });

            const resultado = await respuesta.json();

            Swal.close();

            if (resultado.success) {
                window.location.href = resultado.url;
            } else {
                Swal.fire({
                    title: "Error",
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

                formulario.reset();
            }

        } catch (error) {
            Swal.close();

            Swal.fire({
                title: "Error",
                text: "Ocurrió un problema al conectar con el servidor.",
                icon: "error"
            });

            console.error(error);
        }
    });
});