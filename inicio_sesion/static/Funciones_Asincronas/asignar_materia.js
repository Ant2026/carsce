document.addEventListener("DOMContentLoaded", function() {

    const formulario_asignar_materia = document.getElementById("formulario_asignar_materia");
    const select_nucleos_registrados = document.getElementById("nucleos_registrados");
    const select_pnfs_registrados = document.getElementById("pnfs_registrados");  
    const select_docentes_registrados = document.getElementById("docentes_registrados");

    const contenedorMaterias = document.getElementById("contenedor_materias");

    const dialogo_actualizar_asignacion = document.getElementById("dialogo_docente_asignado_materia");
    const btn_cerrar_dialogo = document.getElementById("cerrar_dialogo");
    const formulario_actualizar_asignacion = document.getElementById("formulario_docente_asignado_materia");
    const input_id_asignacion = document.getElementById("materia_seleccionada");
    const select_docente_asignado = document.getElementById("docentes_asignados");

    let nucleo = "", pnf = "", docente = ""

    function getCookie(nombre) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(nombre + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(nombre.length + 1)
                    );
                    break;
                }
            }
        }

        return cookieValue;
    }
    const csrftoken = getCookie("csrftoken");

    async function obtener_nucleos_registrados() {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();
            
            select_pnfs_registrados.innerHTML = '<option value="">Debe seleccionar un núcleo</option>';

            select_nucleos_registrados.innerHTML = '<option value="">Seleccione un núcleo</option>';

            resultado.nucleos.forEach(nucleo => {
                const opcion = document.createElement("option");
                opcion.value = nucleo.id_nucleo;
                opcion.textContent = nucleo.municipio;
                select_nucleos_registrados.appendChild(opcion);
            });

        } catch (error) {
            console.error(error);
        }
    }   
    obtener_nucleos_registrados();
    
    select_nucleos_registrados.addEventListener("change", async function() {
        nucleo = select_nucleos_registrados.value;
        
        select_pnfs_registrados.disabled = false;
        
        await obtener_pnfs_registrados();
    });

    async function obtener_pnfs_registrados() {
        if (!nucleo) {
            select_pnfs_registrados.innerHTML = '<option value="">Seleccione un P.N.F.</option>';
            return;
        }
        
        try {     
            const formulario = new FormData();
            formulario.append("nucleo", nucleo);

            const respuesta = await fetch("/pnfs_pertenece_nucleo/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            select_pnfs_registrados.innerHTML = '<option value="">Seleccione un P.N.F.</option>';

            resultado.pnfs.forEach(pnf => {
                const opcion = document.createElement("option");
                opcion.value = pnf.id_pnf;
                opcion.textContent = pnf.pnf;
                select_pnfs_registrados.appendChild(opcion);
            });
        } catch (error) {
            console.error(error);
        }
    }
    obtener_pnfs_registrados();

    select_pnfs_registrados.addEventListener("change", async function() {
        pnf = select_pnfs_registrados.value;    
        select_docentes_registrados.disabled = false;

        await obtener_docentes_registrados()
        await obtener_materias_registradas()
    });

    async function obtener_docentes_registrados() {
        try {
            const formulerio = new FormData();
            formulerio.append("nucleo", nucleo);
            formulerio.append("pnf", pnf);

            const respuesta = await fetch("/docentes_registrados/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulerio
            });
            const resultado = await respuesta.json();

            select_docentes_registrados.innerHTML = '<option value="">Selecciona un docente.</option>';

            resultado.usuarios.forEach(usuario => {
                const opcion = document.createElement("option");
                opcion.value = usuario.id_usuario;
                opcion.textContent = usuario.nombres + " " + usuario.apellidos;
                select_docentes_registrados.appendChild(opcion);
            });
        
        } catch (error) {
            console.error(error);
        }  
    }
    obtener_docentes_registrados();

    select_docentes_registrados.addEventListener("change", async function() {
        docente = select_docentes_registrados.value;    
    });

    async function obtener_materias_registradas() {
        if (!pnf) {
            return;
        }

        try {
            const formulario = new FormData();
            formulario.append("pnf", pnf);

            const respuesta = await fetch("/materias_registradas/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });

            const resultado = await respuesta.json();
            console.log(resultado.materias);

            contenedorMaterias.innerHTML = "<h4>Materias Disponibles</h4>";

            resultado.materias.forEach(materia => {

                const div = document.createElement("div");

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "materias";
                checkbox.value = materia.id_materia;
                checkbox.id = "materia_" + materia.id_materia;

                const label = document.createElement("label");
                label.htmlFor = checkbox.id;
                label.textContent = materia.nombre;

                div.appendChild(checkbox);
                div.appendChild(label);

                contenedorMaterias.appendChild(div);

            });

        } catch (error) {
            console.error(error);
        }
    }
    obtener_materias_registradas();
    
    formulario_asignar_materia.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const formData = new FormData(formulario_asignar_materia);

            const respuesta = await fetch("/modulo_asignar_materia_docente/", {
                method: "POST",
                headers: { 
                    "X-CSRFToken": csrftoken
                },
                body: formData
            });
            const resultado = await respuesta.json();

            if (resultado.estado === "success") {
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
            formulario_asignar_materia.reset();
        } catch (error) {
            console.error(error);
        }
    });
});