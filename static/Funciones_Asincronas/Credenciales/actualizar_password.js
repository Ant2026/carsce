document.addEventListener("DOMContentLoaded", () => {
    const formulario_registro = document.getElementById("formulario_registrar");

    formulario_registro.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registro);

            const respuesta = await fetch("/rec_cont/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado === "exito") {
                window.location.href = "/buscar_usuario/";
            } 

            formulario_registro.reset();
        } catch (error) {
            console.error(error);
        }
    });
});