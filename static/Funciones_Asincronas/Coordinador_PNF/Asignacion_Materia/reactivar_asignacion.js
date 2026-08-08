document.addEventListener("DOMContentLoaded", function() {
 
    const select_trayecto = document.getElementById("trayecto");
    const input_materia = document.getElementById("materia");

    const contenedor_materias = document.getElementById("contenedor_materias");

    input_materia.addEventListener("input", async () => {
        await MateriasRegistrada();
    });

    select_trayecto.addEventListener("change", async () => {
       await MateriasRegistrada();
    });

    async function MateriasRegistrada() {
        try {
            const formulario = new FormData();
            formulario.append("trayecto", select_trayecto.value);
            formulario.append("materia", input_materia.value);
            const respuesta = await fetch("/mats_desact/", {
                method: "POST",
                headers: {
                    "X-CSRFToken":
                        document.querySelector(
                            "[name=csrfmiddlewaretoken]"
                        ).value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            contenedor_materias.innerHTML = "";

            // AGRUPAR MATERIAS POR TRAYECTO
            const materias_por_trayecto = {};

            resultado.materias.forEach(materia => {
                if (!materias_por_trayecto[materia.trayecto]) {
                    materias_por_trayecto[materia.trayecto] = [];
                }

                materias_por_trayecto[materia.trayecto].push(materia);
            });

            Object.entries(materias_por_trayecto).forEach(([trayecto, materias]) => {
                const contenedor_trayecto = document.createElement("div");

                // TÍTULO DEL TRAYECTO
                const titulo = document.createElement("h3");
                titulo.textContent = trayecto;

                const tabla =document.createElement("table");
                tabla.classList.add("tabla-materias");
                tabla.innerHTML = `
                    <thead>
                        <tr>
                            <th>N.º</th>
                            <th>MATERIA</th>
                            <th>CÓDIGO</th>
                            <th>SECCIÓN</th>
                            <th>DOCENTE PRINCIPAL</th>
                            <th>DOCENTE SUPLENTE</th>
                            <th>FECHA DE SUSPENSIÓN</th>
                            <th>ESTADO</th>
                        </tr>
                    </thead>
                    <tbody></tbody>`;

                const tbody = tabla.querySelector("tbody");

                // FILAS
                materias.forEach((materia, index) => {
                    const fila = document.createElement("tr");

                    // ID de la asignación.
                    // Se utilizará cuando se seleccione la fila.
                    fila.dataset.id = materia.id_materia_asignada;

                    // DOCENTE PRINCIPAL
                    const nombre_principal = materia.docente_principal ? materia.docente_principal.nombre_completo : "No asignado";

                    // DOCENTE SECUNDARIO
                    const nombre_secundario = materia.docente_secundario ? materia.docente_secundario.nombre_completo : "No asignado";
                    const fecha_suspension = materia.fecha_suspension? new Date(materia.fecha_suspension).toLocaleString("es-VE"): "No registrada";

                    fila.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${materia.nombre}</td>
                        <td>${materia.codigo}</td>
                        <td>${materia.seccion}</td>
                        <td>${nombre_principal}</td>
                        <td>${nombre_secundario}</td>
                        <td>${fecha_suspension}</td>
                        <td>
                            <button
                                type="button"
                                class="btn-reactivar-materia"
                                data-id="${materia.id_materia_asignada}">
                                Reactivar
                            </button>
                        </td>`;

                        tbody.appendChild(fila);
                    });

                contenedor_trayecto.appendChild(titulo);

                contenedor_trayecto.appendChild(tabla);
                contenedor_materias.appendChild(contenedor_trayecto);
            });
        } catch (error) {
            console.error(error);
        }
    }
    MateriasRegistrada();

    document.addEventListener("click", async (e) => {
        const boton = e.target.closest(".btn-reactivar-materia");
        if (!boton) {
            return;
        }
            
        try {
            const formulario = new FormData();
            formulario.append("materia_asignada", boton.dataset.id);

            const respuesta = await fetch("/asig_desact/", {
                method: "POST",
                headers: {
                    "X-CSRFToken":
                        document.querySelector("[name=csrfmiddlewaretoken]").value
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

            await MateriasRegistrada();
        } catch (error) {
            console.error(error);
        }
    });

});