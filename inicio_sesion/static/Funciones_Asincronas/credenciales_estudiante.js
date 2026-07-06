document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("grupo_credenciales").classList.add("oculto");

    select_nacionalidad = document.getElementById("nacionalidad")
    input_cedula = document.getElementById("cedula_identidad")

    const formulario_buscar_estudiante = document.getElementById("formulario_buscar_estudiante")
    const formulario_credenciales_estudiante = document.getElementById("formulario_credenciales_estudiante")

    formulario_buscar_estudiante.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_buscar_estudiante);

            const respuesta = await fetch("/buscar_personal_registrado/", {
                method: "POST",
                body: formulario
            });

            const resultado = await respuesta.json();

            if (resultado.estado === "success") {
                document.getElementById("grupo_buscar").classList.add("oculto");
                document.getElementById("grupo_credenciales").classList.remove("oculto");

                select_nacionalidad.selectedIndex = 0;
                input_cedula.value = "";
                input_cedula.disabled = true;
                input_cedula.placeholder = "Seleccione nacionalidad";

            } else if (resultado.estado === "existe") {
                select_nacionalidad.selectedIndex = 0;
                input_cedula.value = "";
                input_cedula.disabled = true;
                input_cedula.placeholder = "Seleccione nacionalidad";
                
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }  else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }

            formulario_buscar_estudiante.reset();
        } catch (error) {
            Swal.fire({
                text: error,
                icon: "warning",
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        }
    });


    formulario_credenciales_estudiante.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_credenciales_estudiante)
            const respuesta = await fetch("/credenciales_estudiante/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json()

            if (resultado.estado === "success") {
                document.getElementById("grupo_buscar").classList.remove("oculto");
                document.getElementById("grupo_credenciales").classList.add("oculto");

                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            
            formulario_credenciales_estudiante.reset()
        } catch (error) {
            Swal.fire({
                text: error,
                icon: "warning",
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        }
    });
});