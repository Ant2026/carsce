document.addEventListener("DOMContentLoaded", function() {

    const formulario_registrar = document.getElementById("formulario_asignar_materia");
    const select_docentes_registrados = document.getElementById("docentes_registrados");
    const select_secciones_registradas = document.getElementById("secciones_registradas");
    const input_nombre_materia = document.getElementById("nombre_materia");
    const contenedor_materias = document.getElementById("contenedor_materias");
    
    async function obtener_docentes_registrados() {
        try {
            const respuesta = await fetch("/docs_reg/");
            const resultado = await respuesta.json();
            console.log(resultado)

            select_docentes_registrados.innerHTML = '<option value="">Selecciona un docente.</option>';

            resultado.usuarios.forEach(usuario => {
                const opcion = document.createElement("option");
                opcion.value = usuario.id_usuario;
                opcion.textContent = usuario.nombre;
                select_docentes_registrados.appendChild(opcion);
            });
        
        } catch (error) {
            console.error(error);
        }  
    }
    obtener_docentes_registrados();

    async function obtener_secciones_registrados() {
        try {
            const respuesta = await fetch("/sec_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_secciones_registradas.innerHTML = '<option value="">Selecciona la sección.</option>';

            resultado.secciones.forEach(seccion => {
                const opcion = document.createElement("option");
                opcion.value = seccion.id_seccion;
                opcion.textContent = seccion.nombre + " " + seccion.turno;
                select_secciones_registradas.appendChild(opcion);
            });
        } catch (error) {
            console.error(error);
        }  
    }
    obtener_secciones_registrados();
    
    async function obtener_materias_registradas() {
        try {
            const respuesta = await fetch("/mats_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            contenedor_materias.innerHTML = "";

            if (resultado.estado !== "exito") {
                contenedor_materias.innerHTML = `<p>${resultado.descripcion}</p>`;
                return;
            }

            if (resultado.materias.length === 0) {
                contenedor_materias.innerHTML = "<p>No hay materias registradas.</p>";
                return;
            }

            // Agrupar materias por trayecto
            const materiasPorTrayecto = {};

            resultado.materias.forEach(materia => {
                if (!materiasPorTrayecto[materia.trayecto]) {
                    materiasPorTrayecto[materia.trayecto] = [];
                }

                materiasPorTrayecto[materia.trayecto].push(materia);
            });

            // Crear una tabla por cada trayecto
            Object.keys(materiasPorTrayecto).forEach(trayecto => {
                const titulo = document.createElement("h4");
                titulo.textContent = `Trayecto ${trayecto}`;
                contenedor_materias.appendChild(titulo);

                const tabla = document.createElement("table");
                tabla.classList.add("tabla-materias");

                tabla.innerHTML = `
                    <thead>
                        <tr>
                            <th style="width:60px; text-align:center;">
                                Asignar
                            </th>
                            <th>
                                Materia
                            </th>
                        </tr>
                    </thead>

                    <tbody></tbody>
                `;

                const tbody = tabla.querySelector("tbody");

                materiasPorTrayecto[trayecto].forEach(materia => {
                    const fila = document.createElement("tr");

                    // Color según estado de asignación
                    switch (materia.estado) {

                        case "VERDE":
                            fila.classList.add("materia-verde");
                            break;

                        case "AMARILLO":
                            fila.classList.add("materia-amarillo");
                            break;

                        case "ROJO":
                            fila.classList.add("materia-rojo");
                            break;
                    }

                    fila.innerHTML = `
                        <td style="text-align:center;">
                            <input
                                type="checkbox"
                                name="materias[]"
                                value="${materia.id_materia}">
                        </td>
                        <td>
                            ${materia.nombre}
                        </td>
                    `;

                    tbody.appendChild(fila);
                });
                contenedor_materias.appendChild(tabla);
            });
        } catch (error) {
            console.error(error);
            contenedor_materias.innerHTML = `<p>Ocurrió un error al cargar las materias.</p>`;
        }
    }
    obtener_materias_registradas();
    
    formulario_registrar.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/asig_mat_doc/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_registrar.reset();
                await obtener_materias_registradas();
            }
        } catch (error) {
            console.error(error);
        }
    });

});