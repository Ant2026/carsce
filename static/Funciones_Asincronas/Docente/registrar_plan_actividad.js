document.addEventListener("DOMContentLoaded", () => {

    const formulario_plan_estudio = document.getElementById("formulario_registrar");

    const select_nucleo_asignado = document.getElementById("nucleo_asignado");
    const select_pnfs_asignado = document.getElementById("pnfs_asignado");

    const select_asignacion_materia = document.getElementById("asignacion_materia");
    const select_periodo_academico = document.getElementById("periodo_academico");

    const cantidad_evaluaciones = document.getElementById("cantidad_evaluaciones");
    const contenedor_evaluacion = document.getElementById("contenedor_evaluacion");

    const estado_unidades = document.getElementById("estado_unidades");

    let materia, nucleo, pnf;

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

            select_asignacion_materia.innerHTML = "<option value='' selected>Selecciona el pnf primero</option>";

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
    });

    async function materias_asignadas() {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo)
            formulario.append("id_pnf", pnf)

            const respuesta = await fetch("/notas_academicas/mat_asig_doc/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_periodo_academico.innerHTML = "<option value='' selected>Debe seleccionar la materia</option>";

            select_asignacion_materia.innerHTML = "<option value='' selected>Selecciona la materia</option>";

            resultado.datos.forEach(materia => {
                const option_materia = document.createElement("option");
                option_materia.value = materia.id_materia_asignada;
                option_materia.textContent = materia.nombre;
                select_asignacion_materia.append(option_materia);
            });
        } catch (error) {
            console.error(error);
        }
    }

    select_asignacion_materia.addEventListener("change", async () => {
        materia = select_asignacion_materia.value;
        await periodos_academicos();
        await unidades_registradas();
    });

    async function periodos_academicos() {
        try {
            const formulario = new FormData();
            formulario.append("id_asignacion", materia);

            const respuesta = await fetch("/notas_academicas/perd_acad_reg/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_periodo_academico.innerHTML = "<option value='' selected>Selecciona la Periodo Académico</option>";

            resultado.periodos.forEach(periodo => {
                const option_periodo_academico = document.createElement("option");
                option_periodo_academico.value = periodo.id_periodo;
                option_periodo_academico.textContent = periodo.nombre;
                select_periodo_academico.append(option_periodo_academico);
            });
        } catch (error) {
            console.error(error);
        }
    }

    function mostrar_evaluaciones() {
        const cantidad = Number(cantidad_evaluaciones.value);

        contenedor_evaluacion.innerHTML = "";
        if (cantidad === 0) {
            contenedor_evaluacion.innerHTML = `
                <p class="ayuda_evaluaciones">Seleccione la cantidad de evaluaciones que tendrá esta unidad.</p>
            `;
            return;
        }

        for (let i = 1; i <= cantidad; i++) {
            const evaluacion = document.createElement("div");
            evaluacion.classList.add("bloque_evaluacion");

            evaluacion.innerHTML = `
                <h3>Evaluación ${i}</h3>

                <label for="metodo_evaluacion_${i}">Método de Evaluación:</label>
                <input type="text" name="metodo_evaluacion_${i}" id="metodo_evaluacion_${i}" list="metodos_evaluacion_${i}"  maxlength="100" placeholder="Seleccione o escriba un método de evaluación" autocomplete="off" required>

                <datalist id="metodos_evaluacion_${i}">
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

                <label for="fecha_evaluacion_${i}">Fecha de Evaluación:</label>
                <input type="date" name="fecha_evaluacion_${i}" id="fecha_evaluacion_${i}" required>
            `;

            contenedor_evaluacion.appendChild(evaluacion);
        }
    }
    mostrar_evaluaciones();

    cantidad_evaluaciones.addEventListener("change", mostrar_evaluaciones);

    async function unidades_registradas() {
        try {
            const formulario = new FormData();
            formulario.append("id_asignacion", materia);

            const respuesta = await fetch("/notas_academicas/cant_und_reg/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado !== "ok") {
                estado_unidades.innerHTML = `${resultado.mensaje}`;

                estado_unidades.className = "estado_unidades estado_error";
                return;
            }

            const cantidad = resultado.cantidad;
            if (!resultado.existe_plan) {

                estado_unidades.innerHTML = `
                    <strong>Unidades registradas:</strong>0 de 6
                    <span class="separador">|</span>
                    <strong>Mínimo:</strong>4
                    <span class="separador">|</span>
                    <strong>Máximo:</strong>6
                    <p>Aún no se han registrado unidades para esta asignación de materia.</p>
                `;

                estado_unidades.className = "estado_unidades estado_advertencia";
                return;
            }

            estado_unidades.innerHTML = `
                <strong>Unidades registradas:</strong>${cantidad} de 6

                <span class="separador">|</span>
                <strong>Mínimo:</strong>4

                <span class="separador">|</span>
                <strong>Máximo:</strong>6
            `;

            if (cantidad < 4) {
                estado_unidades.className = "estado_unidades estado_advertencia";

                estado_unidades.innerHTML += `<p>El plan aún no cumple con el mínimo de<strong>4 unidades</strong>.</p>`;
            } else if (cantidad >= 4 && cantidad <= 6) {
                estado_unidades.className = "estado_unidades estado_correcto";

                estado_unidades.innerHTML += `
                    <p>El plan cumple con la cantidad de unidades
                    requerida y puede ser enviado al
                    <strong>Coordinador de PNF</strong>
                    para su aprobación.</p>
                `;
            } else {
                estado_unidades.className = "estado_unidades estado_error";

                estado_unidades.innerHTML += `
                    <p>El plan supera el máximo permitido de
                    <strong>6 unidades</strong>.
                    No puede ser enviado para aprobación.</p>
                `;
            }
        } catch (error) {
            console.error(error);
        }
    }

    formulario_plan_estudio.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_plan_estudio);

            const respuesta = await fetch("/notas_academicas/reg_pl_act/", {
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
                formulario_plan_estudio.reset();
                contenedor_evaluacion.innerHTML = "";
            }
        } catch (error) {
            console.error(error);
        }
    });

});