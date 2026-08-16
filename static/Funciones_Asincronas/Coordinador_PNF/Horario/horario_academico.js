document.addEventListener("DOMContentLoaded", () => {
    const formulario_registrar = document.getElementById("formulario_registrar");
    const select_trayectos = document.getElementById("trayectos_registrados");
    const select_periodo_academico = document.getElementById("periodos_academicas_registrados");
    const select_aula_academico = document.getElementById("aulas_registrados");
    const select_seccion_academico = document.getElementById("seccion_registrados");

    const input_cantidad_fila = document.getElementById("cantidad_fila");

    const contenedor_horario = document.getElementById("contenedor_horario");

    const btn_registrar = document.getElementById("generar_pdf");

    let datos_pnf = [];
    let materias = [];
    let trayecto, seccion;

    async function trayectos_registrados() {
        try {
            const respuesta = await fetch("/trayecto_hor/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_trayectos.innerHTML = "<option value='' selected>Selecciona de el trayecto</option>";

            resultado.trayectos.forEach(trayecto => {
                const option_trayecto = document.createElement("option");
                option_trayecto.textContent = trayecto;
                option_trayecto.value = trayecto;
                select_trayectos.appendChild(option_trayecto);
            });
        } catch (error) {
            console.error(error);
        }
    }
    trayectos_registrados();

    select_trayectos.addEventListener("change", async () => {
        trayecto = select_trayectos.value;

        limpiar_horario();

        await periodo_academico_registrados();
    });

    async function periodo_academico_registrados() {
        try {
            const formulario = new FormData();
            formulario.append("trayecto", trayecto)

            const respuesta = await fetch("/periodo_academico_hor/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_periodo_academico.innerHTML = "<option value='' selected>Selecciona el periodo académico</option>";

            resultado.periodos_academicos.forEach(periodo => {
                const option_periodo = document.createElement("option");
                option_periodo.textContent = periodo.nombre;
                option_periodo.value = periodo.id;
                select_periodo_academico.appendChild(option_periodo);
            });
        } catch (error) {
            console.error(error);
        }
    }
    periodo_academico_registrados();

    async function aulas_registradas() {
        try {
            const respuesta = await fetch("/aulas_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            resultado.aulas.forEach(aula => {
                const option_aula = document.createElement("option");
                option_aula.value = aula.id_aula;
                option_aula.textContent = aula.nombre_aula;
                select_aula_academico.append(option_aula);
            });
        } catch (error) {
            console.error(error);
        }
    }
    aulas_registradas();

    async function secciones_registradas() {
        try {
            const respuesta = await fetch("/sec_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            resultado.secciones.forEach(seccion => {
                const option_seccion = document.createElement("option");
                option_seccion.value = seccion.id_seccion;
                option_seccion.textContent = seccion.nombre + " " + seccion.turno;
                select_seccion_academico.append(option_seccion);
            });
        } catch (error) {
            console.error(error);
        }
    }
    secciones_registradas();

    // Validaciones para la tabla horario académico

    function limpiar_horario() {
        materias = [];
        contenedor_horario.innerHTML = "";
        input_cantidad_fila.value = "";
        input_cantidad_fila.disabled = true;
    }

    select_seccion_academico.addEventListener("change", async () => {
        seccion = select_seccion_academico.value;

        limpiar_horario();

        await materias_asignadas();
    });

    // Tabla de horario
    async function materias_asignadas() {
        try {
            const trayecto = select_trayectos.value;
            const seccion = select_seccion_academico.value;
            const aula = select_aula_academico.value;
            const periodo = select_periodo_academico.value;

            if (!trayecto || !seccion || !aula || !periodo || seccion === "undefined") {
                materias = [];
                return;
            }
            input_cantidad_fila.disabled = false;

            const formulario = new FormData();
            formulario.append("trayecto", trayecto);
            formulario.append("seccion", seccion);

            const respuesta = await fetch("/asig_mat_reg/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
                body: formulario,
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            materias = resultado.materias;

        } catch (error) {
            console.error(error);
        }
    }

    // Inhabilita la materia seleccionada al siguiente select
    function actualizar_opciones_materias() {
        const selects = contenedor_horario.querySelectorAll("select");

        const materias_seleccionadas = new Set();

        selects.forEach((select) => {
            if (select.value) {
                materias_seleccionadas.add(select.value);
            }
        });

        selects.forEach((select) => {
            const valor_actual = select.value;

            select.querySelectorAll("option").forEach((option) => {
                if (!option.value) {
                    return;
                }

                option.disabled = materias_seleccionadas.has(option.value) && option.value !== valor_actual;
            });
        });
    }

    input_cantidad_fila.addEventListener("input", async (e) => {
        // Máximo 2 dígitos
        if (input_cantidad_fila.value.length > 2) {
            input_cantidad_fila.value =
                input_cantidad_fila.value.slice(0, 2);
        }

        let cantidad_filas = parseInt(input_cantidad_fila.value);

        // Máximo 5 filas
        if (cantidad_filas > 5) {
            input_cantidad_fila.value = 5;
            cantidad_filas = 5;
        }

        // Evitar valores inválidos
        if (isNaN(cantidad_filas) || cantidad_filas < 1) {
            contenedor_horario.innerHTML = "";
            return;
        }

        // Select
        const valores_actuales = {};
        const selects_actuales = contenedor_horario.querySelectorAll("select");
        selects_actuales.forEach((select) => {
            valores_actuales[select.name] = select.value;
        });

        // Input:time
        const horas_actuales = {};
        const inputs_hora = contenedor_horario.querySelectorAll('input[type="time"]');
        inputs_hora.forEach((input) => {
            horas_actuales[input.name] = input.value;
        });

        await materias_asignadas(); // OBTENER MATERIAS

        // RECONSTRUIR TABLA
        contenedor_horario.innerHTML = "";
        for (let fila = 0; fila < cantidad_filas; fila++) {
            const tr = document.createElement("tr");

            // Input inicio en la tabla 
            const td_inicio = document.createElement("td");
            const input_inicio = document.createElement("input");
            input_inicio.type = "time";
            input_inicio.name = `hora_inicio_${fila}`;

            if (horas_actuales[input_inicio.name]) { // RESTAURAR HORA ANTERIOR
                input_inicio.value = horas_actuales[input_inicio.name];
            }

            td_inicio.appendChild(input_inicio);
            tr.appendChild(td_inicio);

            // Input final en la tabla 
            const td_final = document.createElement("td");
            const input_final = document.createElement("input");
            input_final.type = "time";
            input_final.name = `hora_final_${fila}`;

            if (horas_actuales[input_final.name]) { // RESTAURAR HORA ANTERIOR
                input_final.value = horas_actuales[input_final.name];
            }

            td_final.appendChild(input_final);
            tr.appendChild(td_final);

            // select materias para la tabla
            for (let dia = 0; dia < 5; dia++) {
                const td = document.createElement("td");
                const select = document.createElement("select");
                select.name = `materia_${fila}_${dia}`;

                const opcion_vacia = document.createElement("option"); // vaciar selects
                opcion_vacia.value = "";
                opcion_vacia.textContent = "-- Seleccionar materia --";
                select.appendChild(opcion_vacia);

                materias.forEach((asignacion) => { // materias a select
                    const option = document.createElement("option");
                    option.value = asignacion.id_materia_asignada;
                    option.textContent = `${asignacion.materia.nombre}`;
                    select.appendChild(option);
                });

                if (valores_actuales[select.name]) { // RESTAURAR MATERIA
                    select.value = valores_actuales[select.name];
                }

                select.addEventListener("change", () => { // Validacion, inhabilita materia para los otros
                    actualizar_opciones_materias(); // selects
                });

                td.appendChild(select);
                tr.appendChild(td);
            }
            contenedor_horario.appendChild(tr);
        }
        actualizar_opciones_materias(); // Validacion, inhabilita materia para los otros selects
    });

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/reg_hor/", {
                method: "POST",
                body: formulario,
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false,
            });

            if (resultado.estado === "exito") {
                formulario_registrar.reset();
            }
        } catch (error) {
            console.error(error);
        }
    });
}); 