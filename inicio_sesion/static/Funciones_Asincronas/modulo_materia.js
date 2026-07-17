document.addEventListener("DOMContentLoaded", () => {
    const select_registrar_pnfs = document.getElementById("pnfs_registrar_materia");
    const select_registrar_trayecto = document.getElementById("trayecto_registrar_materia")
    const formulario_registrar = document.getElementById("registrar_materia");
    const contenedor = document.getElementById("contenedor_tablas_materia");

    const dialogo_actualizar = document.getElementById("dialogo_actuailizar_materia");
    const btn_cerrar = document.getElementById("cerrar_dialogo");

    const formulario_actualizar = document.getElementById("actualizar_materia");

    const input_materia_oculta = document.getElementById("materia_seleccionado");
    const input_actualizar_nombre = document.getElementById("nombres_actualizar_materias");
    const input_actualizar_codigo = document.getElementById("codigos_actualizar_materias");
    const select_actualizar_periodo_materia = document.getElementById("periodo_actualizar_materia");
    const select_actualizar_trayecto = document.getElementById("trayecto_actualizar_materia");
    const select_actualizar_recuperacion = document.getElementById("reparacion_actualizar_materia");
    const select_actualizar_pnf = document.getElementById("pnfs_actualizar_materia");

    const select_busqueda_pnf = document.getElementById("buscar_pnf")
    const select_busqueda_trayecto = document.getElementById("buscar_trayecto")

    let pnf = "", trayecto = ""

    async function pnfs_registrados() {
        try {
            const respuesta = await fetch("/pnfs_registrada/")
            const resultado = await respuesta.json()
            select_registrar_pnfs.innerHTML = "<option value='' selected>Seleccionar el P.N.F</option>"
            select_busqueda_pnf.innerHTML = "<option value='' selected>Seleccionar el P.N.F</option>"

            resultado.pnfs.forEach(pnf => {
                const option_registrar = document.createElement("option")
                option_registrar.value = pnf.id_pnf
                option_registrar.textContent = pnf.pnf
                select_registrar_pnfs.appendChild(option_registrar)
                
                const option_actualizar = document.createElement("option")
                option_actualizar.value = pnf.id_pnf
                option_actualizar.textContent = pnf.pnf
                select_actualizar_pnf.appendChild(option_actualizar)
                
                const option_buscar = document.createElement("option")
                option_buscar.value = pnf.id_pnf
                option_buscar.textContent = pnf.pnf
                select_busqueda_pnf.appendChild(option_buscar)
            });
        } catch (error) {
            console.error(error)
        }
    }
    pnfs_registrados();

    async function trayectos_registrados() {
        try {
            const respuesta = await fetch("/trayectos_registrados/")
            const resultado = await respuesta.json()
            
            select_registrar_trayecto.innerHTML = "<option value=''>Seleccionar el Trayecto</option>"
            select_busqueda_trayecto.innerHTML = "<option value=''>Seleccionar el Trayecto</option>"
            
            resultado.trayectos.forEach(trayecto => {
                const option_registrar = document.createElement("option")
                option_registrar.value = trayecto.id_trayecto
                option_registrar.textContent = trayecto.trayecto
                select_registrar_trayecto.appendChild(option_registrar)
                
                const option_actualizar = document.createElement("option")
                option_actualizar.value = trayecto.id_trayecto
                option_actualizar.textContent = trayecto.trayecto
                select_actualizar_trayecto.appendChild(option_actualizar)
                
                const option_buscar = document.createElement("option")
                option_buscar.value = trayecto.id_trayecto
                option_buscar.textContent = trayecto.trayecto
                select_busqueda_trayecto.appendChild(option_buscar)
            });
        } catch (error) {
            console.error(error)
        }
    }
    trayectos_registrados();

    select_busqueda_pnf.addEventListener("change", async () => {
        pnf = select_busqueda_pnf.value;
        await materias_registradas()
    });

    select_busqueda_trayecto.addEventListener("change", async () => {
        trayecto = select_busqueda_trayecto.value;
        await materias_registradas()
    });

    async function materias_registradas() {
        try {
            const formulario = new FormData();
            formulario.append("pnf", pnf);
            formulario.append("trayecto", trayecto);

            const respuesta = await fetch("/materias_almacenada/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            contenedor.innerHTML = "";
            if (!resultado.pnfs || !resultado.materias) {
                return;
            }
            const materiasPorPNF = {};

            resultado.pnfs.forEach(pnf => {
                materiasPorPNF[pnf.id_pnf] = {
                    id: pnf.id_pnf,
                    nombre: pnf.pnf,
                    codigo: pnf.codigo,
                    materias: []
                };
            });
            resultado.materias.forEach(materia => {
                if (materiasPorPNF.hasOwnProperty(materia.id_pnf)) {
                    materiasPorPNF[materia.id_pnf].materias.push(materia);
                }
            });

            Object.values(materiasPorPNF).forEach(pnf => {
                if (pnf.materias.length === 0) {
                    return;
                }
                const tabla = document.createElement("table");
                tabla.classList.add("tabla_materias");

                let filas = "";

                pnf.materias.forEach((materia, index) => {

                    filas += `
                        <tr
                            data-id="${materia.id_materia}"
                            data-id-pnf="${pnf.id}"
                            data-nombre="${materia.nombre}"
                            data-codigo="${materia.codigo}"
                            data-tipo="${materia.tipo_materia}"
                            data-trayecto="${materia.trayecto}"
                            data-recuperacion="${materia.recuperacion}">

                            <td>${index + 1}</td>
                            <td>${materia.nombre}</td>
                            <td>${materia.codigo}</td>
                            <td>${materia.tipo_materia}</td>
                            <td>${materia.trayecto}</td>
                            <td>${materia.recuperacion}</td>
                        </tr>
                    `;
                });

                tabla.innerHTML = `
                    <thead>
                        <tr>
                            <th colspan="6">${pnf.nombre}</th>
                        </tr>

                        <tr>
                            <th>#</th>
                            <th>Materia</th>
                            <th>Código</th>
                            <th>Tipo</th>
                            <th>Trayecto</th>
                            <th>Recuperación</th>
                        </tr>
                    </thead>

                    <tbody>
                        ${filas}
                    </tbody>
                `;

                contenedor.appendChild(tabla);
            });
        } catch (error) {
            console.error(error);
        }
    }
    materias_registradas();

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)
            const respuesta = await fetch("/modulo_materia/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json()

            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                await materias_registradas();
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_registrar.reset()
        } catch (error) {
            console.error(error)
        }
    });

    contenedor.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr");
        if (!fila) return;
        try {
            const formulario = new FormData();
            formulario.append("id_materia", fila.dataset.id);
            formulario.append("id_pnf", fila.dataset.idPnf);

            const respuesta = await fetch("/datos_materia/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            dialogo_actualizar.showModal();
            input_materia_oculta.value = fila.dataset.id

            input_actualizar_nombre.value = resultado.materia.nombre
            input_actualizar_codigo.value = resultado.materia.codigo
            
            const option_periodo_academico = document.createElement("option")
            option_periodo_academico.value = resultado.materia.tipo_materia
            option_periodo_academico.textContent = resultado.materia.tipo_materia
            option_periodo_academico.selected = true
            option_periodo_academico.hidden = true
            select_actualizar_periodo_materia.appendChild(option_periodo_academico)
            
            const option_trayecto = document.createElement("option")
            option_trayecto.value = resultado.trayecto.id_trayecto
            option_trayecto.textContent = resultado.trayecto.trayecto
            option_trayecto.selected = true
            option_trayecto.hidden = true
            select_actualizar_trayecto.appendChild(option_trayecto)
            
            const option_recuperacion = document.createElement("option")
            option_recuperacion.value = resultado.materia.recuperacion
            option_recuperacion.textContent = resultado.materia.recuperacion
            option_recuperacion.selected = true
            option_recuperacion.hidden = true
            select_actualizar_recuperacion.appendChild(option_recuperacion)
            
            const option_pnf = document.createElement("option")
            option_pnf.value = resultado.pnf.id_pnf
            option_pnf.textContent = resultado.pnf.pnf
            option_pnf.selected = true
            option_pnf.hidden = true
            select_actualizar_pnf.appendChild(option_pnf)

        } catch (error) {
            console.error(error);
        }
    });

    btn_cerrar.addEventListener("click", () => {
        dialogo_actualizar.close();
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar)
            const respuesta = await fetch("/guardar_actualizacion_materia/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json()
            console.log(resultado);

            dialogo_actualizar.close()
            if (resultado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            contenedor.innerHTML = "";
            await materias_registradas();
        } catch (error) {
            console.error(error)
        }
    });

});