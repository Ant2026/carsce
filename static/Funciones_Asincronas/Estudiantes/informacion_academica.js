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

        await materias_presentada();

        await plan_estudio();
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
    });

    async function plan_estudio() {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);
            formulario.append("id_pnf", pnf);
            formulario.append("id_materia", materia);

            const respuesta = await fetch("/notas_academicas/plan_act_est/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

        } catch (error) {
            console.error(error);
        }
    }
});