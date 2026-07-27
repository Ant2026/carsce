document.addEventListener("DOMContentLoaded", () => {
    const formulario_registrar = document.getElementById("formulario_registrar");

    const contenedorNucleosControl = document.getElementById("contenedor_nucleos_encargado_control_estudios");
    const contenedorNucleosCoordinador = document.getElementById("contenedor_nucleos_coordinador_pnf");
    const contenedorNucleosDocente = document.getElementById("contenedor_nucleos_docente");
    const contenedorPnfsCoordinador = document.getElementById("contenedor_pnfs_coordinador_pnf");
    const contenedorPnfsDocente = document.getElementById("contenedor_pnfs_docente");

    formulario_registrar.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/pre_registro_personal/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
    
            if (resultado.estado == "exito") {
                formulario_registrar.reset();
                contenedorNucleosControl.innerHTML = ""
                contenedorNucleosCoordinador.innerHTML = ""
                contenedorNucleosDocente.innerHTML = ""
                contenedorPnfsCoordinador.innerHTML = ""
                contenedorPnfsDocente.innerHTML = ""
            }
        } catch (error) {
            console.error(error);
        }
    });

});