document.addEventListener("DOMContentLoaded", () => {

    const contenedor_planes_actividades = document.getElementById("contenedor_planes_actividades");
    const formulario_estado = document.getElementById("formulario_estado");

    const dialogo_planes_estudios = document.getElementById("dialogo_planes_estudios");
    const cerrar_dialogo_visualizar = document.getElementById("cerrar_dialogo_visualizar");

    const dialogo_actualizar_plan_estudio = document.getElementById("dialogo_actualizar_plan_estudio");
    const cerrar_dialogo_actualizar = document.getElementById("cerrar_dialogo_actualizar");
    const formulario_actualizacion = document.getElementById("formulario_actualizacion");

    // controles actualización
    const input_id_plan = document.getElementById("id_plan");
    const input_materia = document.getElementById("materia");
    const input_pnf = document.getElementById("pnf");
    const input_nucleo = document.getElementById("nucleo");
    const input_periodo_academico = document.getElementById("periodo_academico");

    const input_titulo_unidad = document.getElementById("titulo_unidad");
    const textarea_contenido_unidad = document.getElementById("contenido_unidad");

    const contenedor_evaluaciones = document.getElementById("contenedor_evaluaciones");

    const pestanas_unidades_actualizacion = document.getElementById("pestanas_unidades_actualizacion");
    const contenedor_unidades = document.getElementById("contenedor_unidades");

    async function obtenerPlanesActividades() {
        try {
            const response = await fetch("/notas_academicas/pl_reg/");
            const resultado = await response.json();
            console.log(resultado);

            contenedor_planes_actividades.innerHTML = "";
            if (resultado.length === 0) {
                contenedor_planes_actividades.innerHTML = `
                    <tr>
                        <td colspan="5">
                            No hay planes de actividades registrados.
                        </td>
                    </tr>
                `;
                return;
            }

            resultado.datos.forEach((plan, index) => {
                let accion = "";
                if (plan.cantidad_unidades >= 4 && plan.estado_aceptacion === "BORRADOR") {
                    accion = `
                        <button
                            type="button"
                            class="btn-enviar-plan"
                            data-id-plan="${plan.id_plan}">
                            Enviar al Coordinador
                        </button>
                    `;


                }

                let botonEnviar = "";

                if (plan.estado_aceptacion === "DENEGADA") {
                    accion = `
                        <button
                            type="button"
                            class="btn-enviar-plan"
                            data-id-plan="${plan.id_plan}"
                            data-observacion="${plan.observacion}">
                            Enviar nuevamente
                        </button>
                    `;
                }

                const fila = document.createElement("tr");

                // Aquí queda guardado el ID del plan en el TR
                fila.dataset.idPlan = plan.id_plan;
                fila.dataset.estado = plan.estado_aceptacion;
                fila.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${plan.materia}</td>
                    <td>${plan.estado_aceptacion_display}</td>
                    <td>${plan.cantidad_unidades}</td>
                    <td>${accion}</td>
                `;

                contenedor_planes_actividades.appendChild(fila);
            });
        } catch (error) {
            console.error(error);
        }
    }
    obtenerPlanesActividades();

    contenedor_planes_actividades.addEventListener("click", async (e) => {
        const boton = e.target.closest(".btn-enviar-plan");

        if (boton) {
            e.stopPropagation();

            const id_plan = boton.dataset.idPlan;

            const resultado = await Swal.fire({
                title: "¿Enviar plan de actividades?",
                text: "¿Está seguro de enviar este plan de actividades al Coordinador PNF?",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: "Sí, enviar",
                cancelButtonText: "Cancelar",
                reverseButtons: true
            });

            if (resultado.isConfirmed) {
                await coordinador_pnf(id_plan);
            }

            return;
        }




        // CLICK EN LA FILA
        const fila = e.target.closest("tr");

        if (fila && fila.dataset.idPlan) {
            const id_plan = fila.dataset.idPlan;
            const estado = fila.dataset.estado;

            if (estado === "ACEPTADA" || estado === "ENVIADO") {
                await Swal.fire({
                    title: "Plan aceptado",
                    text: "Este plan ya fue aceptado y no puede ser modificado.",
                    icon: "info",
                    confirmButtonText: "Visualizar"
                });

                await plan_estudio(id_plan);

                return;
            }

            if (estado === "DENEGADA") {

                const observacion = fila.dataset.observacion || "";

                const resultado = await Swal.fire({
                    title: "Plan de actividades denegado",

                    html: `
                <div style="text-align: left;">

                    <p>
                        El Coordinador PNF ha denegado este plan de actividades.
                    </p>

                    <div style="
                        margin-top: 15px;
                        padding: 15px;
                        border-radius: 8px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                    ">

                        <strong>Observación:</strong>

                        <p style="
                            margin-top: 8px;
                            margin-bottom: 0;
                            white-space: pre-wrap;
                        ">
                            ${observacion || "No se registró una observación."}
                        </p>

                    </div>

                </div>
            `,

                    icon: "warning",

                    showCancelButton: true,

                    confirmButtonText: "Modificar plan",

                    cancelButtonText: "Cerrar",

                    reverseButtons: true
                });

                if (resultado.isConfirmed) {
                    await actualizar_plan_estudio(id_plan);
                }

                return;
            }

            const resultado = await Swal.fire({
                title: "¿Qué desea hacer?",
                text: "Seleccione una opción para el plan de actividades.",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: "Visualizar",
                cancelButtonText: "Modificar",
                reverseButtons: true
            });


            if (resultado.isConfirmed) {
                await plan_estudio(id_plan);
            } else if (resultado.dismiss === Swal.DismissReason.cancel) {
                await actualizar_plan_estudio(id_plan);
            }

        }
    });

    async function plan_estudio(id_plan) {
        try {
            const formulario = new FormData();
            formulario.append("id_plan", id_plan);

            const response = await fetch("/notas_academicas/datos_pl_reg/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await response.json();
            console.log(resultado);

            if (!resultado.datos) {
                console.error("No se recibieron datos del plan.");
                return;
            }

            const plan = resultado.datos;

            const informacion_plan = document.getElementById("informacion_plan");
            const pestanas_unidades = document.getElementById("pestanas_unidades");
            const contenido_unidades = document.getElementById("contenido_unidades");

            informacion_plan.innerHTML = `
                <p><strong>Materia:</strong>${plan.materia}</p>
                <p><strong>PNF:</strong>${plan.pnf} </p>
                <p><strong>Núcleo:</strong>${plan.nucleo}</p>
                <p><strong>Período:</strong>${plan.periodo_academico} </p>
            `;

            pestanas_unidades.innerHTML = "";
            contenido_unidades.innerHTML = "";


            plan.detalles.forEach((detalle, indice) => {
                const pestana = document.createElement("button");
                pestana.type = "button";
                pestana.className = "pestana_unidad";
                pestana.textContent = detalle.titulo_unidad;
                pestana.dataset.idDetalle = detalle.id_detalle;

                // Primera unidad activa
                if (indice === 0) {
                    pestana.classList.add("activa");
                }
                pestanas_unidades.appendChild(pestana);


                const contenido = document.createElement("div");
                contenido.className = "contenido_unidad";
                contenido.dataset.idDetalle = detalle.id_detalle;

                // Ocultar todas excepto la primera
                if (indice !== 0) {
                    contenido.style.display = "none";
                }

                let evaluacionesHTML = "";

                if (detalle.evaluaciones && detalle.evaluaciones.length > 0) {
                    detalle.evaluaciones.forEach(evaluacion => {
                        evaluacionesHTML += `
                            <div class="evaluacion">
                                <div class="evaluacion_info">
                                    <strong>${evaluacion.metodo_evaluacion}</strong>
                                    <span>${evaluacion.fecha_evaluacion}</span>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    evaluacionesHTML = `<p class="sin_evaluaciones">No hay evaluaciones registradas.</p> `;
                }

                contenido.innerHTML = `
                    <h4>${detalle.titulo_unidad}</h4>
                    <div class="dato_unidad">
                        <strong>Ponderación:</strong>
                        <span>${detalle.ponderacion}</span>
                    </div>

                    <div class="contenido_unidad_texto">
                        <strong>Contenido:</strong>
                        <p>${detalle.contenido_unidad}</p>
                    </div>

                    <div class="seccion_evaluaciones">
                        <h4>
                            Evaluaciones
                        </h4>
                        <div class="evaluaciones_unidad">
                            ${evaluacionesHTML}
                        </div>
                    </div>
                `;

                contenido_unidades.appendChild(contenido);
            });

            document.querySelectorAll(".pestana_unidad").forEach(pestana => {
                pestana.addEventListener("click", () => {
                    const idDetalle = pestana.dataset.idDetalle;

                    // QUITAR PESTAÑA ACTIVA
                    document.querySelectorAll(".pestana_unidad").forEach(p => {
                        p.classList.remove("activa");
                    });

                    // OCULTAR CONTENIDOS
                    document.querySelectorAll(".contenido_unidad").forEach(contenido => {
                        contenido.style.display = "none";
                    });

                    pestana.classList.add("activa");

                    const contenido = document.querySelector(`.contenido_unidad[data-id-detalle="${idDetalle}"]`);
                    if (contenido) {
                        contenido.style.display = "block";
                    }
                });
            });

            dialogo_planes_estudios.showModal();
        } catch (error) {
            console.error(error);
        }
    }

    cerrar_dialogo_visualizar.addEventListener("click", () => {
        dialogo_planes_estudios.close();
    });

    async function actualizar_plan_estudio(id_plan) {
        try {
            const formulario = new FormData();
            formulario.append("id_plan", id_plan);

            const response = await fetch("/notas_academicas/datos_pl_reg/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await response.json();
            console.log(resultado);

            dialogo_actualizar_plan_estudio.showModal();

            input_id_plan.value = resultado.datos.id_plan;
            input_materia.value = resultado.datos.materia;
            input_nucleo.value = resultado.datos.nucleo;
            input_pnf.value = resultado.datos.pnf;
            input_periodo_academico.value = resultado.datos.periodo_academico;

            pestanas_unidades_actualizacion.innerHTML = "";
            contenedor_unidades.innerHTML = "";

            // CREAR UNIDADE
            resultado.datos.detalles.forEach((detalle, i) => {
                const numeroUnidad = i + 1;

                // CREAR PESTAÑA
                const pestana = document.createElement("button");
                pestana.type = "button";
                pestana.classList.add("pestana_unidad_actualizacion");
                pestana.textContent = `Unidad ${numeroUnidad}`;

                /* Primera pestaña activa */
                if (i === 0) {
                    pestana.classList.add("activa");
                }

                pestanas_unidades_actualizacion.appendChild(pestana);

                // CREAR CONTENIDO DE LA UNIDAD
                const unidad = document.createElement("div");
                unidad.classList.add("unidad_contenido_actualizacion");
                if (i === 0) {
                    unidad.classList.add("activa");
                }


                unidad.innerHTML = `
                    <input type="hidden"  name="id_detalle_${i}" value="${detalle.id_detalle || ""}">

                    <label for="titulo_unidad_${i}">Título de la Unidad:<label>

                    <input type="text" name="titulo_unidad_${i}" id="titulo_unidad_${i}" maxlength="100"
                        value="${detalle.titulo_unidad || ""}" autocomplete="off" required>

                    <label for="contenido_unidad_${i}">Contenido de la Unidad:</label>
                    <textarea name="contenido_unidad_${i}" id="contenido_unidad_${i}"  required
                    >${detalle.contenido_unidad || ""}</textarea>

                    <h4>Evaluaciones</h4>
                    <div  id="contenedor_evaluaciones_${i}" class="contenedor_evaluaciones_actualizacion"></div>
                `;
                contenedor_unidades.appendChild(unidad);

                // CONTENEDOR DE EVALUACIONES
                const contenedorEvaluaciones =
                    unidad.querySelector(
                        `#contenedor_evaluaciones_${i}`
                    );

                // CREAR EVALUACIONES
                detalle.evaluaciones.forEach((evaluacion, j) => {

                    const indice = `${i}_${j}`;

                    const contenedor = document.createElement("div");

                    contenedor.classList.add("evaluacion_actualizar");

                    contenedor.innerHTML = `
                        <input
                            type="hidden"
                            name="id_evaluacion_${indice}"
                            value="${evaluacion.id_evaluacion || ""}">

                        <div class="evaluacion_cabecera">
                            <h4>Evaluación ${j + 1}</h4>
                        </div>

                        <div class="campo_formulario">
                            <label for="metodo_evaluacion_${indice}">
                                Método de Evaluación:
                            </label>
                            <input
                                type="text"
                                name="metodo_evaluacion_${indice}"
                                id="metodo_evaluacion_${indice}"
                                list="metodos_evaluacion_${indice}"
                                maxlength="100"
                                placeholder="Seleccione o escriba un método de evaluación"
                                autocomplete="off"
                                value="${evaluacion.metodo_evaluacion || ""}"
                                required>

                            <datalist id="metodos_evaluacion_${indice}">
                                <option value="Prueba escrita">
                                <option value="Exposición">
                                <option value="Taller">
                                <option value="Debate">
                                <option value="Práctica">
                                <option value="Ensayo">
                                <option value="Investigación">
                                <option value="Proyecto">
                                <option value="Seminario">
                                <option value="Estudio de caso">
                                <option value="Portafolio">
                            </datalist>
                        </div>

                        <div class="campo_formulario">
                            <label for="fecha_evaluacion_${indice}">
                                Fecha de Evaluación:
                            </label>
                            <input
                                type="date"
                                name="fecha_evaluacion_${indice}"
                                id="fecha_evaluacion_${indice}"
                                value="${evaluacion.fecha_evaluacion || ""}"
                                required>
                        </div>`;

                    contenedorEvaluaciones.appendChild(contenedor);
                });

                const controlesEvaluaciones = document.createElement("div");
                controlesEvaluaciones.classList.add("controles_evaluaciones");

                controlesEvaluaciones.innerHTML = `
                    <button type="button" class="btn_agregar_evaluacion">
                        + Agregar evaluación
                    </button>

                    <button type="button" class="btn_eliminar_evaluacion">
                        Eliminar evaluación
                    </button>
                `;

                unidad.appendChild(controlesEvaluaciones);

                const botonAgregar = controlesEvaluaciones.querySelector(".btn_agregar_evaluacion");

                botonAgregar.addEventListener("click", () => {

                    const evaluaciones = contenedorEvaluaciones.querySelectorAll(".evaluacion_actualizar");
                    if (evaluaciones.length >= 2) {
                        return;
                    }

                    const indice = evaluaciones.length;
                    const contenedor = document.createElement("div");

                    contenedor.classList.add("evaluacion_actualizar");


                    contenedor.innerHTML = `
                            <div class="evaluacion_cabecera">
                                <h4>Evaluación ${indice + 1}</h4>
                            </div>

                            <div class="campo_formulario">
                                <label for="metodo_evaluacion_${i}_${indice}">
                                    Método de Evaluación:
                                </label>

                                <input
                                    type="text"
                                    name="metodo_evaluacion_${i}_${indice}"
                                    id="metodo_evaluacion_${i}_${indice}"
                                    list="metodos_evaluacion_${i}_${indice}"
                                    maxlength="100"
                                    placeholder="Seleccione o escriba un método de evaluación"
                                    autocomplete="off"
                                    required>

                                <datalist id="metodos_evaluacion_${i}_${indice}">
                                    <option value="Prueba escrita">
                                    <option value="Exposición">
                                    <option value="Taller">
                                    <option value="Debate">
                                    <option value="Práctica">
                                    <option value="Ensayo">
                                    <option value="Investigación">
                                    <option value="Proyecto">
                                    <option value="Seminario">
                                    <option value="Estudio de caso">
                                    <option value="Portafolio">
                                </datalist>
                            </div>

                            <div class="campo_formulario">
                                <label for="fecha_evaluacion_${i}_${indice}">
                                    Fecha de Evaluación:
                                </label>
                                <input
                                    type="date"
                                    name="fecha_evaluacion_${i}_${indice}"
                                    id="fecha_evaluacion_${i}_${indice}"
                                    required>
                            </div>
                        `;

                    contenedorEvaluaciones.appendChild(contenedor);
                    actualizarControles();

                }
                );

                const botonEliminar = controlesEvaluaciones.querySelector(".btn_eliminar_evaluacion");

                botonEliminar.addEventListener("click", () => {
                    const evaluaciones = contenedorEvaluaciones.querySelectorAll(".evaluacion_actualizar");

                    if (evaluaciones.length <= 1) {
                        return;
                    }

                    const segunda = evaluaciones[1];
                    const inputId = segunda.querySelector('input[name^="id_evaluacion_"]');

                    // Si existe en BD
                    if (inputId && inputId.value) {
                        const inputEliminar = document.createElement("input");

                        inputEliminar.type = "hidden";
                        inputEliminar.name = "eliminar_evaluacion[]";
                        inputEliminar.value = inputId.value;
                        formulario_actualizacion.appendChild(
                            inputEliminar
                        );
                    }
                    segunda.remove();
                    actualizarControles();
                });

                function actualizarControles() {
                    const cantidad =
                        contenedorEvaluaciones.querySelectorAll(
                            ".evaluacion_actualizar"
                        ).length;

                    botonAgregar.disabled = cantidad >= 2;
                    botonEliminar.disabled = cantidad <= 1;
                }

                // CAMBIAR DE PESTAÑA
                pestana.addEventListener("click", () => {
                    document
                        .querySelectorAll(
                            ".pestana_unidad_actualizacion"
                        )
                        .forEach(p => {
                            p.classList.remove("activa");
                        });

                    document
                        .querySelectorAll(
                            ".unidad_contenido_actualizacion"
                        )
                        .forEach(u => {
                            u.classList.remove("activa");
                        });

                    pestana.classList.add("activa");

                    unidad.classList.add("activa");
                });
            });
        } catch (error) {
            console.error(error);
        }
    }

    cerrar_dialogo_actualizar.addEventListener("click", () => {
        dialogo_actualizar_plan_estudio.close();
    });

    async function coordinador_pnf(plan_estudio) {
        try {
            const formulario = new FormData();
            formulario.append("id_plan", plan_estudio);

            const response = await fetch("/notas_academicas/env_pla/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await response.json();
            console.log(resultado);

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            await obtenerPlanesActividades();
        } catch (error) {
            console.error(error);
        }
    }

    formulario_actualizacion.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizacion);

            const respuesta = await fetch("/notas_academicas/act_pl_reg/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            dialogo_actualizar_plan_estudio.close();

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                contenedor_evaluaciones.innerHTML = "";
            }
        } catch (error) {
            console.error(error);
        }
    });

});