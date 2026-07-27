document.addEventListener("DOMContentLoaded", () => {
    const formulario_PNF = document.getElementById("formulario_PNF_estudiante")

    formulario_PNF.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const respuesta = await fetch("/registrar_pnfs_cursar/", {
                method: "POST",
                body: new FormData(formulario_PNF)
            });
            const resultado = await respuesta.json()

             if (resultado.estado === "success") {
                window.location.href = "/registro_documento/";
            } else {
                Swal.fire({
                    title: resultado.titulo,
                    text: resultado.descripcion,
                    icon: resultado.icon,
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