document.addEventListener("DOMContentLoaded", () => {

    const select_pnf_asignado = document.getElementById("pnf_asignado");
    const contenedor_planes_actividades = document.getElementById("contenedor_planes_actividades");

    const dialogo_coordinador_planes_estudios = document.getElementById("dialogo_coordinador_planes_estudios");
    const cerrar_dialogo = document.getElementById("cerrar_dialogo");

    let pnf_seleccionado;

    async function pnf_asignado() {
        try {
            const respuesta = await fetch("/pnf_asig_coord/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_pnf_asignado.innerHTML = "<option value='' selected>Selecciona el PNF</option>";

            resultado.pnfs.forEach(pnf => {
                const option_pnf = document.createElement("option");
                option_pnf.value = pnf.id_pnf;
                option_pnf.textContent = pnf.pnf;
                select_pnf_asignado.append(option_pnf);
            });
        } catch (error) {
            console.error(error);
        }
    }
    pnf_asignado();

    select_pnf_asignado.addEventListener("change", async (e) => {
        pnf_seleccionado = select_pnf_asignado.value;
        await obtenerPlanesActividades();
    });

    contenedor_planes_actividades.innerHTML = `
        <tr>
            <td colspan="5">
                Debe seleccionar un P.N.F seleccionado.
            </td>
        </tr>
    `;

    async function obtenerPlanesActividades() {
        try {
            const formulario = new FormData();
            formulario.append("pnf_asignado", pnf_seleccionado);

            const response = await fetch("/pl_reg_coord_pnf/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await response.json();
            console.log(resultado);

            contenedor_planes_actividades.innerHTML = "";
            if (resultado.datos.length === 0) {
                contenedor_planes_actividades.innerHTML = `
                    <tr>
                        <td colspan="5">
                            No hay planes de actividades enviados.
                        </td>
                    </tr>
                `;
                return;
            }

            resultado.datos.forEach(plan => {
                const fila = document.createElement("tr");
                fila.dataset.idPlan = plan.id_plan;

                fila.innerHTML = `
                    <td>${plan.id_plan}</td>
                    <td>${plan.materia}</td>
                    <td>${plan.periodo_academico}</td>
                    <td>${plan.cantidad_unidades}</td>
                    <td>
                        <button
                            type="button"
                            class="btn-aceptar-plan"
                            data-id-plan="${plan.id_plan}"
                            data-estado="ACEPTADA">
                            ACEPTADA
                        </button>

                        <button
                            type="button"
                            class="btn-denegar-plan"
                            data-id-plan="${plan.id_plan}"
                            data-estado="DENEGADA">
                            DENEGADA
                        </button>
                    </td>
                `;

                contenedor_planes_actividades.appendChild(fila);
            });
        } catch (error) {
            console.error(error);
        }
    }

    contenedor_planes_actividades.addEventListener("click", async (e) => {
        const boton = e.target.closest("button");

        if (boton) {

            const id_plan = boton.dataset.idPlan;
            const estado = boton.dataset.estado;

            if (!id_plan || !estado) return;

            console.log("ID del plan:", id_plan);
            console.log("Botón presionado:", estado);

            const confirmacion = await Swal.fire({
                title: estado === "ACEPTADA"
                    ? "¿Aceptar plan de actividades?"
                    : "¿Denegar plan de actividades?",

                text: estado === "ACEPTADA"
                    ? "¿Está seguro de que desea aceptar este plan?"
                    : "¿Está seguro de que desea denegar este plan?",

                input: "textarea",
                inputLabel: "Observación",
                inputPlaceholder: estado === "ACEPTADA"
                    ? "Escriba una observación..."
                    : "Indique el motivo de la denegación...",

                inputAttributes: {
                    "aria-label": "Observación"
                },

                showCancelButton: true,
                confirmButtonText: estado === "ACEPTADA"
                    ? "Aceptar plan"
                    : "Denegar plan",
                cancelButtonText: "Cancelar",

                allowOutsideClick: false,
                allowEscapeKey: false,

                inputValidator: (observacion) => {
                    if (!observacion.trim()) {
                        return "Debe ingresar una observación.";
                    }
                }
            });

            if (!confirmacion.isConfirmed) {
                return;
            }

            const observacion = confirmacion.value.trim();

            await cambiar_estado(id_plan, estado, observacion);
            return;
        }

        const fila = e.target.closest("tr");
        if (!fila) return;

        const id_plan = fila.dataset.idPlan;
        if (!id_plan) return;

        await plan_estudio(id_plan);
    });

    async function plan_estudio(id_plan) {
        try {
            const formulario = new FormData();
            formulario.append("id_plan", id_plan);

            const response = await fetch("/datos_pl_reg_coord_pnf/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await response.json();
            console.log(resultado);

            const datos = resultado.datos;

            /* =====================================================
            INFORMACIÓN GENERAL DEL PLAN
            ===================================================== */

            const informacion_plan = document.getElementById(
                "informacion_plan"
            );

            informacion_plan.innerHTML = "";

            const informacion = document.createElement("div");
            informacion.className = "datos_plan";

            const crearDato = (titulo, valor) => {
                const dato = document.createElement("div");
                dato.className = "dato_plan";

                const etiqueta = document.createElement("span");
                etiqueta.className = "etiqueta";
                etiqueta.textContent = titulo;

                const contenido = document.createElement("span");
                contenido.className = "valor";
                contenido.textContent = valor ?? "No disponible";

                dato.appendChild(etiqueta);
                dato.appendChild(contenido);

                return dato;
            };

            informacion.appendChild(
                crearDato("PNF: ", datos.pnf)
            );

            informacion.appendChild(
                crearDato("Núcleo: ", datos.nucleo)
            );

            informacion.appendChild(
                crearDato("Materia: ", datos.materia)
            );

            informacion.appendChild(
                crearDato(
                    "Período académico: ",
                    datos.periodo_academico
                )
            );

            informacion.appendChild(
                crearDato(
                    "Docente: ",
                    datos.docente || "No asignado"
                )
            );

            informacion.appendChild(
                crearDato(
                    "Cédula de Identidad: ",
                    datos.cedula_docente || "No disponible"
                )
            );

            informacion.appendChild(
                crearDato(
                    "Fecha de creación: ",
                    datos.fecha_creacion
                )
            );

            informacion.appendChild(
                crearDato(
                    "Fecha de actualización: ",
                    datos.fecha_actualizacion
                )
            );

            informacion_plan.appendChild(informacion);


            /* =====================================================
            PESTAÑAS Y CONTENIDO DE LAS UNIDADES
            ===================================================== */

            const pestanas_unidades = document.getElementById(
                "pestanas_unidades"
            );

            const contenido_unidades = document.getElementById(
                "contenido_unidades"
            );

            pestanas_unidades.innerHTML = "";
            contenido_unidades.innerHTML = "";


            /* =====================================================
            SIN UNIDADES
            ===================================================== */

            if (!datos.detalles || datos.detalles.length === 0) {

                const mensaje = document.createElement("div");
                mensaje.className = "sin_unidades";
                mensaje.textContent =
                    "No existen unidades académicas registradas.";

                contenido_unidades.appendChild(mensaje);

            } else {

                datos.detalles.forEach((detalle, indice) => {

                    /* =================================================
                    CREAR PESTAÑA
                    ================================================= */

                    const pestana = document.createElement("button");

                    pestana.type = "button";
                    pestana.className = "pestana_unidad";
                    pestana.dataset.indice = indice;

                    if (indice === 0) {
                        pestana.classList.add("activa");
                    }

                    pestana.textContent = detalle.titulo_unidad;

                    pestanas_unidades.appendChild(pestana);


                    /* =================================================
                    CREAR CONTENIDO DE LA UNIDAD
                    ================================================= */

                    const unidad = document.createElement("div");

                    unidad.className = "contenido_unidad";
                    unidad.dataset.indice = indice;

                    if (indice !== 0) {
                        unidad.style.display = "none";
                    }


                    /* =================================================
                    TÍTULO
                    ================================================= */

                    const titulo = document.createElement("h4");

                    titulo.textContent = detalle.titulo_unidad;

                    unidad.appendChild(titulo);


                    /* =================================================
                    PONDERACIÓN
                    ================================================= */

                    const ponderacion = document.createElement("p");

                    ponderacion.innerHTML =
                        `<strong>Ponderación:</strong> ${detalle.ponderacion}`;

                    unidad.appendChild(ponderacion);


                    /* =================================================
                    CONTENIDO
                    ================================================= */

                    const titulo_contenido = document.createElement("h5");

                    titulo_contenido.textContent =
                        "Contenido de la unidad";

                    unidad.appendChild(titulo_contenido);


                    const contenido = document.createElement("div");

                    contenido.className = "texto_contenido";

                    contenido.textContent =
                        detalle.contenido_unidad;

                    unidad.appendChild(contenido);

                    // Evaluacion
                    const titulo_evaluaciones = document.createElement("h5");

                    titulo_evaluaciones.textContent = "Evaluaciones";
                    unidad.appendChild(titulo_evaluaciones);


                    if (!detalle.evaluaciones || detalle.evaluaciones.length === 0) {

                        const mensaje = document.createElement("p");
                        mensaje.textContent = "No existen evaluaciones registradas.";
                        unidad.appendChild(mensaje);
                    } else {
                        const lista = document.createElement("div");

                        lista.className = "lista_evaluaciones";
                        detalle.evaluaciones.forEach((evaluacion) => {
                            const evaluacion_elemento = document.createElement("div");
                            evaluacion_elemento.className = "evaluacion";

                            const metodo = document.createElement("p");
                            metodo.innerHTML =
                                `<strong>Método de evaluación:</strong> ${evaluacion.metodo_evaluacion
                                }`;


                            const fecha = document.createElement("p");
                            fecha.innerHTML =
                                `<strong>Fecha de evaluación:</strong> ${evaluacion.fecha_evaluacion
                                }`;


                            evaluacion_elemento.appendChild(metodo);
                            evaluacion_elemento.appendChild(fecha);
                            lista.appendChild(evaluacion_elemento);
                        }
                        );


                        unidad.appendChild(lista);
                    }


                    contenido_unidades.appendChild(unidad);


                    /* =================================================
                    EVENTO DE LA PESTAÑA
                    ================================================= */

                    pestana.addEventListener("click", () => {

                        pestanas_unidades
                            .querySelectorAll(".pestana_unidad")
                            .forEach((elemento) => {
                                elemento.classList.remove("activa");
                            });

                        contenido_unidades
                            .querySelectorAll(".contenido_unidad")
                            .forEach((elemento) => {
                                elemento.style.display = "none";
                            });


                        pestana.classList.add("activa");

                        unidad.style.display = "block";
                    });

                });
            }


            dialogo_coordinador_planes_estudios.showModal();
        } catch (error) {
            console.error(error);
        }
    }

    cerrar_dialogo.addEventListener("click", () => {
        dialogo_coordinador_planes_estudios.close();
    });

    async function cambiar_estado(id_plan, estado, observacion) {
        try {
            const formulario = new FormData();
            formulario.append("id_plan", id_plan);
            formulario.append("estado", estado);
            formulario.append("observacion", observacion);

            const respuesta = await fetch("/camb_est_pl/", {
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

            if (resultado.estado === "exito") {
                await obtenerPlanesActividades();
            }
        } catch (error) {
            console.error(error);
        }
    }
});