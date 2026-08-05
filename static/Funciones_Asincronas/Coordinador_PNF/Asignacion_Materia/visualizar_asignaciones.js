document.addEventListener("DOMContentLoaded", function() {
    
    const dialogo_actualizar_asignacion = document.getElementById("dialogo_actualizar");
    const btn_cerrar_dialogo = document.getElementById("cerrar_dialogo");
    const formulario_actualizar = document.getElementById("formulario_actualizar");

    const input_id_asignacion = document.getElementById("materia_seleccionada");
    const select_docentes_asignados = document.getElementById("docentes_asignados");

    const contenedor_materias = document.getElementById("contenedor_materias");

    async function obtener_docentes_registrados() {
        try {
            const respuesta = await fetch("/docs_reg/");
            const resultado = await respuesta.json();
            console.log(resultado)

            select_docentes_asignados.innerHTML = '<option value="">Selecciona un docente.</option>';

            resultado.usuarios.forEach(usuario => {
                const opcion = document.createElement("option");
                opcion.value = usuario.id_asignacion;
                opcion.textContent = usuario.nombres + " " + usuario.apellidos;
                select_docentes_asignados.appendChild(opcion);
            });
        
        } catch (error) {
            console.error(error);
        }  
    }
    obtener_docentes_registrados();

    async function obtener_materias_registradas() {
        try {
            const respuesta = await fetch("/mats_reg/");
            const resultado = await respuesta.json();

            contenedor_materias.innerHTML = "";

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


            // Crear tabla por cada trayecto
            Object.keys(materiasPorTrayecto).forEach(trayecto => {
                const titulo = document.createElement("h4");
                titulo.textContent = trayecto;
                contenedor_materias.appendChild(titulo);

                const tabla = document.createElement("table");
                tabla.className = "tabla-materias";

                tabla.innerHTML = `
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Código</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                `;

                const tbody = tabla.querySelector("tbody");

                materiasPorTrayecto[trayecto].forEach(materia => {
                    const fila = document.createElement("tr");
                    fila.dataset.id = materia.id_materia;
                    fila.innerHTML = `
                        <td>
                            ${materia.nombre}
                        </td>

                        <td>
                            ${materia.codigo}
                        </td>
                    `;
                    tbody.appendChild(fila);
                });

                contenedor_materias.appendChild(tabla);
            });
        } catch(error) {
            console.error(error);
        }
    }

    obtener_materias_registradas();
    
    document.addEventListener("click", async (e) => {

        const fila = e.target.closest(".tabla-materias tbody tr");

        if (!fila) return;

        const id_materia = fila.dataset.id;

        console.log(id_materia);

    });

    formulario_actualizar.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/modulo_asignar_materia_docente/", {
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
        } catch (error) {
            console.error(error);
        }
    });


});