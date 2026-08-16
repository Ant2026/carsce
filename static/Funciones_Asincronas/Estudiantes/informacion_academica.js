document.addEventListener("DOMContentLoaded", () => {

    const select_nucleo_presentar = document.getElementById("nucleo_presentar");
    const select_pnfs_cursar = document.getElementById("pnfs_cursar");
    const select_materias_presentadas = document.getElementById("materias_presentadas");
    const select_plan_evaluacion = document.getElementById("plan_evaluacion");

    const contendor_unidades = document.getElementById("contendor_unidades");
    const contenedor_notas_academica = document.getElementById("contenedor_notas_academica");

    let materia, pnf, nucleo;

    async function nucleos_asignados() {
        try {
            const respuesta = await fetch("/notas_academicas/nucleos_est_asig/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_pnfs_cursar.innerHTML = "<option value='' selected>Selecciona el núcleo primero</option>";

            select_nucleo_presentar.innerHTML = "<option value='' selected>Selecciona un núcleo</option>";

            resultado.nucleos.forEach(nucleo => {
                const option_nucleo = document.createElement("option");
                option_nucleo.value = nucleo.id_nucleo;
                option_nucleo.textContent = nucleo.municipio;
                select_nucleo_presentar.append(option_nucleo);
            });
        } catch (error) {
            console.error(error);
        }
    }
    nucleos_asignados();

    select_nucleo_presentar.addEventListener("change", async (e) => {
        nucleo = select_nucleo_presentar.value;

        console.log(nucleo);

        await pnfs_asignados();
    });

    async function pnfs_asignados() {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);

            const respuesta = await fetch("/notas_academicas/pnfs_est_asig/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_materias_presentadas.innerHTML = "<option value='' selected>Selecciona el pnf primero</option>";

            select_pnfs_cursar.innerHTML = "<option value='' selected>Selecciona un P.N.F</option>";

            resultado.pnfs.forEach(pnf => {
                const option_pnf = document.createElement("option");
                option_pnf.value = pnf.id_pnf;
                option_pnf.textContent = pnf.pnf;
                select_pnfs_cursar.append(option_pnf);
            });
        } catch (error) {
            console.error(error);
        }
    }

    select_pnfs_cursar.addEventListener("change", async (e) => {
        pnf = select_pnfs_cursar.value;

        console.log(pnf);

        await materias_presentada();

        await plan_estudio();

        await notas_academicas();
    });

    async function materias_presentada() {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);

            console.log(pnf)
            console.log(nucleo)

            const respuesta = await fetch("/notas_academicas/mate_tray_est/", {
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

            select_materias_presentadas.innerHTML = "<option value='' selected>Selecciona la materia</option>";

            resultado.materias.forEach(materia => {
                const option_materia = document.createElement("option");
                option_materia.value = materia.id_materia;
                option_materia.textContent = materia.nombre;
                select_materias_presentadas.append(option_materia);
            });
        } catch (error) {
            console.error(error);
        }
    }

    select_materias_presentadas.addEventListener("change", async () => {
        const opcion = select_materias_presentadas.selectedOptions[0];

        materia = opcion.value;

        await plan_estudio();

        await notas_academicas();
    });

    async function plan_estudio() {
        try {
            if (!nucleo || !pnf || !materia) return;

            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);
            formulario.append("id_materia", materia);

            const respuesta = await fetch("/notas_academicas/plan_act_est/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    ).value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            const contenedor = document.getElementById("contendor_unidades");

            // LIMPIAR CONTENEDOR
            contenedor.innerHTML = "";

            // MENSAJES DE ERROR
            if (resultado.estado === "fallo") {
                Swal.fire({
                    icon: resultado.icon,
                    title: resultado.title,
                    text: resultado.descripcion
                });

                return;
            }

            // NO EXISTE PLAN
            if (resultado.estado === "no_exite") {
                contenedor.innerHTML = `
                    <table class="tabla_plan_estudio">
                        <thead>
                            <tr>
                                <th>Unidad</th>
                                <th>Ponderación</th>
                                <th>Contenido</th>
                                <th>Método de evaluación</th>
                                <th>Fecha de evaluación</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr>
                                <td colspan="5" class="mensaje_tabla">
                                    ${resultado.descripcion}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                `;

                return;
            }
            // PLAN EXISTENTE
            if (resultado.estado === "exito") {

                let filas = "";

                resultado.unidades.forEach((unidad) => {
                    const evaluaciones = unidad.evaluaciones;

                    // SIN EVALUACIONES
                    if (evaluaciones.length === 0) {
                        filas += `
                            <tr>
                                <td>${unidad.titulo_unidad}</td>
                                <td>${unidad.ponderacion}</td>
                                <td>${unidad.contenido_unidad}</td>
                                <td colspan="2">
                                    Sin evaluaciones registradas
                                </td>
                            </tr>
                        `;
                        return;
                    }

                    // CON EVALUACIONES
                    evaluaciones.forEach((evaluacion, indice) => {

                        filas += `<tr>`;

                        // SOLO MOSTRAR LOS DATOS DE LA UNIDAD EN LA PRIMERA FILA
                        if (indice === 0) {

                            filas += `
                            <td rowspan="${evaluaciones.length}">
                                ${unidad.titulo_unidad}
                            </td>

                            <td rowspan="${evaluaciones.length}">
                                ${unidad.ponderacion}
                            </td>

                            <td rowspan="${evaluaciones.length}">
                                ${unidad.contenido_unidad}
                            </td>
                        `;
                        }

                        // DATOS DE LA EVALUACIÓN
                        filas += `
                        <td>
                            ${evaluacion.metodo_evaluacion}
                        </td>

                        <td>
                            ${evaluacion.fecha_evaluacion}
                        </td>
                    `;
                        filas += `</tr>`;
                    });
                });

                contenedor.innerHTML = `
                <table class="tabla_plan_estudio">
                    <thead>
                        <tr>
                            <th>Unidad</th>
                            <th>Ponderación</th>
                            <th>Contenido</th>
                            <th>Método de evaluación</th>
                            <th>Fecha de evaluación</th>
                        </tr>
                    </thead>

                    <tbody>
                        ${filas}
                    </tbody>
                </table>
            `;
            }

        } catch (error) {
            console.error(error);
        }
    }

    async function notas_academicas() {
        try {
            if (!nucleo || !pnf || !materia) return;

            const formulario = new FormData();

            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);
            formulario.append("id_materia", materia);

            const respuesta = await fetch("/notas_academicas/eval_reg_est/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    ).value
                },
                body: formulario
            });

            const resultado = await respuesta.json();

            console.log(resultado);

            const contenedor = document.getElementById(
                "contenedor_notas_academica"
            );

            // LIMPIAR CONTENEDOR
            contenedor.innerHTML = "";

            // ==========================================
            // ERROR
            // ==========================================

            if (resultado.estado === "fallo") {

                Swal.fire({
                    icon: resultado.icon,
                    title: resultado.title,
                    text: resultado.descripcion
                });

                return;
            }

            // ==========================================
            // NO TIENE CALIFICACIONES
            // ==========================================

            if (resultado.registradas === false) {

                contenedor.innerHTML = `
                    <table class="tabla_notas_academicas">
                        <thead>
                            <tr>
                                <th>Unidad</th>
                                <th>Nota de la unidad</th>
                                <th>Fecha de calificación</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr>
                                <td colspan="3" class="mensaje_tabla">
                                    El estudiante todavía no tiene calificaciones registradas.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                `;

                return;
            }

            // ==========================================
            // TIENE CALIFICACIONES
            // ==========================================

            if (resultado.registradas === true) {

                let filas = "";

                resultado.evaluaciones.forEach((evaluacion) => {

                    filas += `
                        <tr>
                            <td>
                                ${evaluacion.titulo_unidad}
                            </td>

                            <td>
                                ${evaluacion.nota_unidad}
                            </td>

                            <td>
                                ${evaluacion.fecha_calificacion}
                            </td>
                        </tr>
                    `;
                });

                contenedor.innerHTML = `
                    <div class="resumen_notas_academicas">

                        <div class="dato_nota">
                            <span>Trayecto</span>
                            <strong>${resultado.trayecto}</strong>
                        </div>

                        <div class="dato_nota">
                            <span>Promedio</span>
                            <strong>${resultado.promedio_tramo}</strong>
                        </div>

                        <div class="dato_nota">
                            <span>Asistencia</span>
                            <strong>${resultado.asistencia}</strong>
                        </div>

                        <div class="dato_nota">
                            <span>Condición</span>
                            <strong>${resultado.condicion}</strong>
                        </div>

                    </div>

                    <table class="tabla_notas_academicas">

                        <thead>
                            <tr>
                                <th>Unidad</th>
                                <th>Nota de la unidad</th>
                                <th>Fecha de calificación</th>
                            </tr>
                        </thead>

                        <tbody>
                            ${filas}
                        </tbody>

                    </table>
                `;
            }

        } catch (error) {
            console.error(error);
        }
    }


});