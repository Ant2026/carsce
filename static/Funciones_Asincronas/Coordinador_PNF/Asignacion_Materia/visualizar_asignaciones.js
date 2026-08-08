document.addEventListener("DOMContentLoaded", function() {
    
    const dialogo_actualizar_asignacion = document.getElementById("dialogo_actualizar");
    const btn_cerrar_dialogo = document.getElementById("cerrar_dialogo");
    const formulario_actualizar = document.getElementById("formulario_actualizar");
    const input_id_asignacion = document.getElementById("materia_seleccionada");
    
    const select_trayecto = document.getElementById("trayecto");
    const input_materia = document.getElementById("materia");

    const input_actualizar_id = document.getElementById("materia_asignada");
    const input_actualizar_nombre_materia = document.getElementById("nombre_materia");
    const input_actualizar_nombre_seccion = document.getElementById("nombre_seccion");
    
    const input_actualizar_docente_principal_nombre = document.getElementById("docente_principal_nombre");
    const input_radius_principal_activo = document.getElementById("principal_activo");
    const input_radius_principal_inactivo = document.getElementById("principal_inactivo");

    const input_actualizar_docente_secundario_nombre = document.getElementById("docente_secundario_nombre");
    const input_radius_secundario_activo = document.getElementById("secundario_activo");
    const input_radius_secundario_inactivo = document.getElementById("secundario_inactivo");

    const input_radius_materia_activa = document.getElementById("materia_activa");
    const input_radius_materia_suspendida = document.getElementById("materia_suspendida");

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

            const respuesta = await fetch("/mat_asig/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            contenedor_materias.innerHTML = "";

            // Agrupar materias por trayecto
            const materias_por_trayecto = {};
            resultado.materias.forEach(materia => {
                if (!materias_por_trayecto[materia.trayecto]) {
                    materias_por_trayecto[materia.trayecto] = [];
                }
                materias_por_trayecto[materia.trayecto].push(materia);
            });

            // Crear una tabla por cada trayecto
            Object.entries(materias_por_trayecto).forEach(([trayecto, materias]) => {
                    const contenedor_trayecto = document.createElement("div");

                    const titulo = document.createElement("h3");
                    titulo.textContent = trayecto;

                    const tabla = document.createElement("table");
                    tabla.classList.add("tabla-materias");
                    tabla.innerHTML = `
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>MATERIA</th>
                                <th>CÓDIGO</th>
                                <th>SECCIÓN</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    `;

                    const tbody = tabla.querySelector("tbody");
                    
                    materias.forEach((materia, index) => {
                        const fila = document.createElement("tr");
                        fila.dataset.id = materia.id_materia_asignada;

                        fila.innerHTML = `
                            <td>${index + 1}</td>
                            <td>${materia.nombre}</td>
                            <td>${materia.codigo}</td>
                            <td>${materia.seccion}</td>
                        `;
                        tbody.appendChild(fila);
                    });

                    contenedor_trayecto.appendChild(titulo);
                    contenedor_trayecto.appendChild(tabla);
                    contenedor_materias.appendChild(contenedor_trayecto);
                }
            );
        } catch (error) {
            console.error(error);
        }
    }
    MateriasRegistrada();

    document.addEventListener("click", async (e) => {
        const fila = e.target.closest(".tabla-materias tbody tr");
        if (!fila) return;

        try {
            const formulario = new FormData();
            formulario.append("id_asignacion", fila.dataset.id);

            const respuesta = await fetch("/busc_mat/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado === "fallo") {
                await Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    title: resultado.title,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                return;
            }

            const materia = resultado.materia;

            dialogo_actualizar_asignacion.showModal();

            input_actualizar_id.value = materia.id_materia_asignada;
            input_actualizar_nombre_materia.value = materia.nombre;
            input_actualizar_nombre_seccion.value = materia.seccion;

            const docente_principal = materia.docentes.find(docente => docente.rol === "PRINCIPAL");

            const docente_secundario = materia.docentes.find(docente => docente.rol === "SECUNDARIO");

            if (docente_principal) {
                input_actualizar_docente_principal_nombre.value = docente_principal.nombre_completo;
                input_radius_principal_activo.checked =  docente_principal.activo;
                input_radius_principal_inactivo.checked = !docente_principal.activo;
            } else {
                input_actualizar_docente_principal_nombre.value = "";
                input_radius_principal_activo.checked = false;
                input_radius_principal_inactivo.checked = false;
            }

            if (docente_secundario) {
                input_actualizar_docente_secundario_nombre.value = docente_secundario.nombre_completo;
                input_radius_secundario_activo.checked = docente_secundario.activo;
                input_radius_secundario_inactivo.checked = !docente_secundario.activo;

                input_radius_secundario_activo.disabled = false;
                input_radius_secundario_inactivo.disabled = false;
            } else {
                input_actualizar_docente_secundario_nombre.value = "No asignado";
                input_radius_secundario_activo.checked = false;
                input_radius_secundario_inactivo.checked = false;

                input_radius_secundario_activo.disabled = true;
                input_radius_secundario_inactivo.disabled = true;
            }

            input_radius_materia_activa.checked = materia.activo;
            input_radius_materia_suspendida.checked = !materia.activo;

            if (materia.activo && docente_principal && !docente_secundario) {
                input_radius_principal_activo.disabled = false;
                input_radius_principal_inactivo.disabled = true;
                input_radius_principal_activo.checked =  true;
                input_radius_principal_inactivo.checked = false;
            } else {
                input_radius_principal_activo.disabled = false;
                input_radius_principal_inactivo.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    });

    // CAMBIO DE ESTADO DE LA MATERIA
    input_radius_materia_activa.addEventListener("change", () => {
        if (!input_radius_materia_activa.checked) {
            return;
        }

        const existe_secundario = input_actualizar_docente_secundario_nombre.value.trim() !== "" &&
            input_actualizar_docente_secundario_nombre.value.trim() !== "No asignado";

        // NO EXISTE SECUNDARIO
        if (!existe_secundario) {
            input_radius_principal_activo.checked = true;
            input_radius_principal_inactivo.checked = false;
            
            input_radius_principal_inactivo.disabled =  true;

            input_radius_secundario_activo.disabled = true;
            input_radius_secundario_inactivo.disabled = true;
            return;
        }

        // EXISTE SECUNDARIO
        input_radius_principal_inactivo.disabled = false;
        input_radius_secundario_activo.disabled = false;
        input_radius_secundario_inactivo.disabled = false;
    });

    // MATERIA SUSPENDIDA
    input_radius_materia_suspendida.addEventListener("change", () => {
        if (!input_radius_materia_suspendida.checked) {
            return;
        }

        // Los docentes quedan inactivos. La materia está suspendida.
        input_radius_principal_activo.checked = false;
        input_radius_principal_inactivo.checked = true;

        if (input_actualizar_docente_secundario_nombre.value.trim() !== "" &&
            input_actualizar_docente_secundario_nombre.value.trim() !== "No asignado") {
            input_radius_secundario_activo.checked = false;

            input_radius_secundario_inactivo.checked = true;
        } else {
            input_radius_secundario_activo.checked = false;
            input_radius_secundario_inactivo.checked = false;
        }

        input_radius_principal_inactivo.disabled = false;

        if (input_actualizar_docente_secundario_nombre.value.trim() === "" ||
            input_actualizar_docente_secundario_nombre.value.trim() === "No asignado") {
            input_radius_secundario_activo.disabled = true;

            input_radius_secundario_inactivo.disabled = true;
        } else {
            input_radius_secundario_activo.disabled = false;
            input_radius_secundario_inactivo.disabled = false;
        }
    });

    // PRINCIPAL ACTIVO
    input_radius_principal_activo.addEventListener("change", () => {
        if (!input_radius_principal_activo.checked) {
            return;
        }

        const existe_secundario = input_actualizar_docente_secundario_nombre.value.trim() !== "" &&
            input_actualizar_docente_secundario_nombre.value.trim() !== "No asignado";

        if (!existe_secundario) {
            input_radius_principal_activo.checked = true;
            input_radius_principal_inactivo.checked = false;

            input_radius_principal_inactivo.disabled = true;
            return;
        }

        input_radius_secundario_activo.checked = false; // Principal activo
        input_radius_secundario_inactivo.checked = true; // Secundario inactivo
    });

    // PRINCIPAL INACTIVO
    input_radius_principal_inactivo.addEventListener("change",  () => {
        if (!input_radius_principal_inactivo.checked) {
            return;
        }

        const existe_secundario = input_actualizar_docente_secundario_nombre.value.trim() !== "" &&
            input_actualizar_docente_secundario_nombre.value.trim() !== "No asignado";

        if (!existe_secundario) {
            input_radius_principal_activo.checked = true; // No existe suplente.
            input_radius_principal_inactivo.checked = false; // El principal debe permanecer activo.
            return;
        } 

        input_radius_secundario_activo.checked = true; // Principal inactivo
        input_radius_secundario_inactivo.checked = false; // Secundario activo
    });

    formulario_actualizar.addEventListener("submit", async function(e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/act_asig/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            dialogo_actualizar_asignacion.close();

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

    btn_cerrar_dialogo.addEventListener("click", () => {
        dialogo_actualizar_asignacion.close();
    });

});