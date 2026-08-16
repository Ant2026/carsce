document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registrar");

    const select_nucleo_asignado = document.getElementById("nucleo_asignado");
    const select_pnfs_asignado = document.getElementById("pnf_asignado");
    const select_materia_asignada = document.getElementById("materia_asignada");
    const select_periodo_academico = document.getElementById("periodo_academico");
    const input_trayecto_academico = document.getElementById("trayecto_academico");

    const contenedor_notas_academicas = document.getElementById("contenedor_notas_academicas");

    let materia, pnf, nucleo, periodo_academico, cantidad_evaluaciones;

    async function nucleos_asignados() {
        try {
            const respuesta = await fetch("/notas_academicas/nucl_asig_doc/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_pnfs_asignado.innerHTML = "<option value='' selected>Selecciona el núcleo primero</option>";

            select_nucleo_asignado.innerHTML = "<option value='' selected>Selecciona un núcleo</option>";

            resultado.datos.forEach(nucleo => {
                const option_nucleo = document.createElement("option");
                option_nucleo.value = nucleo.id_nucleo;
                option_nucleo.textContent = nucleo.municipio;
                select_nucleo_asignado.append(option_nucleo);
            });
        } catch (error) {
            console.error(error);
        }
    }
    nucleos_asignados();

    select_nucleo_asignado.addEventListener("change", async (e) => {
        nucleo = select_nucleo_asignado.value;

        await pnfs_asignados();

        await calificaciones_materia();
    });

    async function pnfs_asignados() {
        try {
            const formulario = new FormData();
            formulario.append("nucleo_asignado", nucleo);

            const respuesta = await fetch("/notas_academicas/pnfs_asig_doc/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_materia_asignada.innerHTML = "<option value='' selected>Selecciona el pnf primero</option>";

            select_pnfs_asignado.innerHTML = "<option value='' selected>Selecciona un P.N.F</option>";

            resultado.datos.forEach(pnf => {
                const option_pnf = document.createElement("option");
                option_pnf.value = pnf.id_pnf;
                option_pnf.textContent = pnf.pnf;
                select_pnfs_asignado.append(option_pnf);
            });
        } catch (error) {
            console.error(error);
        }
    }

    select_pnfs_asignado.addEventListener("change", async (e) => {
        pnf = select_pnfs_asignado.value;

        await materias_asignadas();

        await calificaciones_materia();
    });

    async function materias_asignadas() {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);

            const respuesta = await fetch("/notas_academicas/mat_not_acad/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });

            const resultado = await respuesta.json();
            console.log(resultado);

            select_periodo_academico.innerHTML = "<option value='' selected>Debe seleccionar la materia</option>";

            select_materia_asignada.innerHTML = "<option value='' selected>Selecciona la materia</option>";

            resultado.datos.forEach(materia => {
                const option_materia = document.createElement("option");
                option_materia.value = materia.id_materia_asignada;
                option_materia.textContent = materia.nombre;
                option_materia.dataset.trayecto = materia.trayecto;
                select_materia_asignada.append(option_materia);
            });

        } catch (error) {
            console.error(error);
        }
    }

    select_materia_asignada.addEventListener("change", async () => {
        const opcion = select_materia_asignada.selectedOptions[0];
        materia = opcion.value;
        const trayecto = opcion.dataset.trayecto;
        input_trayecto_academico.value = trayecto;

        await periodos_academicos();

        await calificaciones_materia();
    });

    async function periodos_academicos() {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);
            formulario.append("id_materia_asignada", materia);

            const respuesta = await fetch("/notas_academicas/per_not_acad/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_periodo_academico.innerHTML = "<option value='' selected>Selecciona un P.N.F</option>";

            resultado.datos.forEach(periodo => {
                const option_periodo = document.createElement("option");
                option_periodo.value = periodo.id_periodo_materia;
                option_periodo.textContent = periodo.nombre;
                select_periodo_academico.append(option_periodo);
            });
        } catch (error) {
            console.error(error);
        }
    }

    select_periodo_academico.addEventListener("change", async (e) => {
        periodo_academico = select_periodo_academico.value;

        await calificaciones_materia();
    });

    async function calificaciones_materia() {
        try {
            if (!nucleo || !pnf || !materia) return;

            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);
            formulario.append("id_materia_asignada", materia);

            const [respuestaEstudiantes, respuestaActividades] = await Promise.all([
                fetch("/notas_academicas/est_not_acad/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: formulario
                }),

                fetch("/notas_academicas/cant_det_pla/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: formulario
                })
            ]);
            const [resultadoEstudiantes, resultadoActividades] = await Promise.all([
                respuestaEstudiantes.json(),
                respuestaActividades.json()
            ]);

            contenedor_notas_academicas.innerHTML = "";
            if (!resultadoEstudiantes.estudiantes || resultadoEstudiantes.estudiantes.length === 0) {
                contenedor_notas_academicas.innerHTML = `
                    <p>No hay estudiantes registrados para esta materia.</p>
                `;
                return;
            }

            const cantidadActividades = resultadoActividades.cantidad_actividades;
            cantidad_evaluaciones = resultadoActividades.cantidad_actividades;

            const tabla = document.createElement("table");
            tabla.classList.add("tabla-calificaciones");

            // Encabezado
            let encabezado = `
                <tr>
                    <th>#</th>
                    <th>Estudiante</th>
                    <th>C.I</th>
            `;

            for (let i = 1; i <= cantidadActividades; i++) {
                encabezado += `
                    <th>Unidad ${i}</th>
                `;
            }

            encabezado += `
                    <th>Asistencia</th>
                    <th>Promedio</th>
                </tr>
            `;

            tabla.innerHTML = `
                <thead>
                    ${encabezado}
                </thead>
                <tbody></tbody>
            `;
            const tbody = tabla.querySelector("tbody");

            resultadoEstudiantes.estudiantes.forEach((estudiante, indice) => {
                const fila = document.createElement("tr");

                let controles = "";

                for (let i = 1; i <= cantidadActividades; i++) {
                    controles += `
                        <td>
                            <input
                                type="text"
                                class="input-calificacion"
                                name="calificacion_${estudiante.id_estudiante}_${i}"
                                data-id-estudiante="${estudiante.id_estudiante}"
                                data-actividad="${i}"
                                min="0"
                                max="20"
                                maxlength="2"
                                step="0.01"
                                placeholder="0 - 20">
                        </td>
                    `;
                }

                fila.innerHTML = `
                    <td>${indice + 1}</td>
                    <td>${estudiante.nombre_completo}</td>
                    <td>${estudiante.cedula}</td>
                    ${controles}
                    <td class="celda-asistencia">
                        <input
                            type="text"
                            class="input-asistencia"
                            name="asistencia_${estudiante.id_estudiante}"
                            data-id-estudiante="${estudiante.id_estudiante}"
                            min="0"
                            max="100"
                            maxlength="3"
                            step="1"
                            placeholder="%"
                        >
                    </td>
                    <td class="celda-promedio">
                        <input
                            type="text"
                            class="input-promedio"
                            name="promedio_${estudiante.id_estudiante}"
                            data-id-estudiante="${estudiante.id_estudiante}"
                            readonly
                        >
                    </td>
                `;

                tbody.appendChild(fila);
            });

            contenedor_notas_academicas.appendChild(tabla);
        } catch (error) {
            console.error(error);
        }
    }

    contenedor_notas_academicas.addEventListener("input", function (e) {
        const input = e.target;

        if (input.classList.contains("input-calificacion")) { // CALIFICACIONES

            input.value = input.value.replace(/[^0-9.]/g, ""); // Solo números y punto
            const partes = input.value.split("."); // Solo un punto

            if (partes.length > 2) {
                input.value = partes[0] + "." + partes.slice(1).join("");
            }

            if (partes.length === 2) { // Maximo 2 descimales
                input.value =
                    partes[0] + "." + partes[1].substring(0, 2);
            }

            if (input.value !== "") { // Máximo 20
                const valor = parseFloat(input.value);
                if (valor > 20) {
                    input.value = "20";
                }
            }
        }

        // CALCULAR PROMEDIO DEL ESTUDIANTE
        const idEstudiante = input.dataset.idEstudiante;

        const calificaciones = contenedor_notas_academicas.querySelectorAll(
            `.input-calificacion[data-id-estudiante="${idEstudiante}"]`
        );

        let suma = 0;
        let cantidad = 0;

        calificaciones.forEach(calificacion => {
            if (calificacion.value !== "") {
                const valor = parseFloat(calificacion.value);
                if (!isNaN(valor)) {
                    suma += valor;
                    cantidad++;
                }
            }
        });

        const promedio = cantidad > 0 ? suma / cantidad : 0;

        // Buscar promedio del mismo estudiante
        const inputPromedio = contenedor_notas_academicas.querySelector(
            `.input-promedio[data-id-estudiante="${idEstudiante}"]`
        );

        if (inputPromedio) {
            inputPromedio.value = cantidad > 0 ? promedio.toFixed(2) : "";
        }

        // ASISTENCIA
        if (input.classList.contains("input-asistencia")) {
            input.value = input.value.replace(/[^0-9]/g, ""); // Solo números
            if (input.value !== "") { // Máximo 100
                const valor = parseInt(input.value);
                if (valor > 100) {
                    input.value = "100";
                }
            }
        }
    });

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);
            formulario.append("cantidad_evaluaciones", cantidad_evaluaciones);

            const respuesta = await fetch("/notas_academicas/reg_nota_acad/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado)

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_registrar.reset();
                contenedor_notas_academicas.innerHTML = "";
            }
        } catch (error) {
            console.error(error);
        }
    });

});