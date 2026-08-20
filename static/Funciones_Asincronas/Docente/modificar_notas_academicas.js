document.addEventListener("DOMContentLoaded", () => {

    const formulario_actualizar = document.getElementById("formulario_actualizar");

    const select_nucleo_asignado = document.getElementById("nucleo_asignado");
    const select_pnfs_asignado = document.getElementById("pnf_asignado");
    const select_materia_asignada = document.getElementById("materia_asignada");
    const input_periodo_academico = document.getElementById("periodo_academico");
    const input_trayecto_academico = document.getElementById("trayecto_academico");

    const contenedor_notas_academicas = document.getElementById("contenedor_notas_academicas");

    let materia, pnf, nucleo, cantidad_evaluaciones;

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

        await materias_registradas();

        await calificaciones_materia();
    });

    async function materias_registradas() {
        try {
            const formulario = new FormData();
            formulario.append("id_pnf", pnf);

            const respuesta = await fetch("/notas_academicas/mod_mat_not/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_materia_asignada.innerHTML = "<option value='' selected>Selecciona la materia</option>";

            resultado.materias.forEach(materia => {
                const option_materia = document.createElement("option");
                option_materia.value = materia.id_materia_asignada;
                option_materia.textContent = materia.nombre_materia;
                option_materia.dataset.trayecto = materia.trayecto_materia;
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

        await periodo_academico();

        await calificaciones_materia();
    });

    async function periodo_academico() {
        try {
            const formulario = new FormData();
            formulario.append("id_pnf", pnf);
            formulario.append("id_materia_asignada", materia);

            const respuesta = await fetch("/notas_academicas/mod_per_not/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado == "fallo") {
                await Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    title: resultado.title,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                return;
            }

            input_periodo_academico.value = resultado.nombre_periodo;

            input_periodo_academico.dataset.idPeriodo = resultado.id_periodo_academico;
        } catch (error) {
            console.error(error);
        }
    }

    async function calificaciones_materia() {
        try {
            if (!nucleo || !pnf || !materia) return;

            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);
            formulario.append("id_materia_asignada", materia);
            formulario.append("id_periodo_academico", input_periodo_academico.dataset.idPeriodo);

            const [respuestaEstudiantes, respuestaActividades] = await Promise.all([
                fetch("/notas_academicas/mod_calf_not/", {
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

            console.log("Cantidad:", resultadoActividades.cantidad_actividades);
            console.log("Calificaciones:", resultadoEstudiantes);

            contenedor_notas_academicas.innerHTML = "";
            if (!resultadoEstudiantes.calificaciones || resultadoEstudiantes.calificaciones.length === 0) {
                contenedor_notas_academicas.innerHTML = `
                    <p>No hay estudiantes registrados para esta materia.</p>
                `;
                return;
            }

            const cantidadActividades = resultadoActividades.cantidad_actividades;
            cantidad_evaluaciones = cantidadActividades;

            const tabla = document.createElement("table");
            tabla.classList.add("tabla-calificaciones");

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

            resultadoEstudiantes.calificaciones.forEach((estudiante, indice) => {
                const fila = document.createElement("tr");

                let controles = "";
                for (let i = 1; i <= cantidadActividades; i++) {
                    const unidad = estudiante.unidades[i - 1];
                    const notaUnidad = unidad ? unidad.nota_unidad : "";

                    controles += `
                            <td class="celda-calificacion">
                                <input
                                    type="text"
                                    class="input-calificacion"
                                    name="calificacion_${estudiante.id_estudiante}_${i}"
                                    data-id-estudiante="${estudiante.id_estudiante}"
                                    data-numero-unidad="${i}"
                                    value="${notaUnidad}"
                                >
                            </td>`;
                }

                fila.innerHTML = `
                        <td>${indice + 1}</td>
                        <td>${estudiante.nombre_estudiante}</td>
                        <td>${estudiante.cedula_identidad}</td>
                        ${controles}
                        <td class="celda-asistencia">
                            <input
                                type="text"
                                class="input-asistencia"
                                name="asistencia_${estudiante.id_estudiante}"
                                data-id-estudiante="${estudiante.id_estudiante}"
                                value="${estudiante.asistencia ?? ""}">
                        </td>

                        <td class="celda-promedio">
                            <input
                                type="text"
                                class="input-promedio"
                                name="promedio_${estudiante.id_estudiante}"
                                data-id-estudiante="${estudiante.id_estudiante}"
                                value="${estudiante.promedio ?? ""}"
                                readonly>
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

        // CALIFICACIONES
        if (input.classList.contains("input-calificacion")) {
            input.value = input.value.replace(/[^0-9.]/g, "");
            const partes = input.value.split(".");

            if (partes.length > 2) {
                input.value =
                    partes[0] + "." + partes.slice(1).join("");
            }

            const partesDecimal = input.value.split(".");
            if (partesDecimal.length === 2) {
                input.value =
                    partesDecimal[0] + "." +
                    partesDecimal[1].substring(0, 2);
            }

            if (input.value !== "") {
                const valor = parseFloat(input.value);
                if (!isNaN(valor) && valor > 20) {
                    input.value = "20";
                }
            }
        }

        // ASISTENCIA
        if (input.classList.contains("input-asistencia")) {
            input.value = input.value.replace(/[^0-9]/g, "");
            if (input.value !== "") {
                const valor = parseInt(input.value);

                if (!isNaN(valor) && valor > 100) {
                    input.value = "100";
                }
            }
        }

        // CALCULAR PROMEDIO DEL ESTUDIANTE
        const idEstudiante = input.dataset.idEstudiante;
        if (!idEstudiante) {
            return;
        }

        const calificaciones = contenedor_notas_academicas.querySelectorAll(
            `.input-calificacion[data-id-estudiante="${idEstudiante}"]`
        );

        let suma = 0;
        let cantidad = 0;
        calificaciones.forEach(calificacion => {
            if (calificacion.value.trim() !== "") {
                const valor = parseFloat(calificacion.value);

                if (!isNaN(valor)) {
                    suma += valor;
                    cantidad++;
                }
            }
        });

        const promedio = cantidad > 0 ? suma / cantidad : 0;

        const inputPromedio = contenedor_notas_academicas.querySelector(
            `.input-promedio[data-id-estudiante="${idEstudiante}"]`
        );

        if (inputPromedio) {
            inputPromedio.value = cantidad > 0 ? Math.round(promedio) : "";
        }
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizar);
            formulario.append("id_periodo_academico", input_periodo_academico.dataset.idPeriodo);

            const respuesta = await fetch("/notas_academicas/mod_not_acad/", {
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
                formulario_actualizar.reset();
                contenedor_notas_academicas.innerHTML = "";
            }
        } catch (error) {
            console.error(error);
        }
    });

});