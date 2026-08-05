document.addEventListener("DOMContentLoaded", () => {
    const formulario_buscar = document.getElementById("formulario_buscar_usuario");

    const nacionalidad = document.getElementById("nacionalidad");
    const cedula_identidad = document.getElementById("cedula_identidad");

    configurarCedula(nacionalidad, cedula_identidad);

    formulario_buscar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_buscar);

            const respuesta = await fetch("/bus_usr/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.estado === "exito") {
                window.location.href = "/comp_usr/";
            } else {
                Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }

            formulario_buscar.reset();
        } catch (error) {
            console.error(error);
        }
    });
});