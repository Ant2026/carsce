document.addEventListener("DOMContentLoaded", () => {
    const formulario_autenticacion = document.getElementById("formulario_login");

    formulario_autenticacion.addEventListener("submit", async function (e) {
        e.preventDefault();

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
            const formulario = new FormData(formulario_autenticacion);

            const respuesta = await fetch("/inicio_sesion/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            Swal.close();

            if (resultado.estado == "exito") {
                window.location.href = resultado.url;
            } else {
                Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_autenticacion.reset();
        } catch (error) {
            Swal.close();
            console.error(error);
        }
    });
});