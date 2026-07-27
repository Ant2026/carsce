document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registrar_seccion")
    const select_registrar_nucleo = document.getElementById("registro_nucleo_registrado")
    const select_registrar_pnf = document.getElementById("registro_pnf_registrado")
    const select_registrar_trayecto = document.getElementById("registro_trayecto_registrado")
    const select_registrar_aula = document.getElementById("registro_aula_registrado")
    const select_registrar_turno = document.getElementById("registrar_turno")
    const input_registrar_seccion = document.getElementById("registrar_seccion")

    const contenedor_secciones = document.getElementById("tabla_secciones")
    const dialogo_actualizar = document.getElementById("dialogo_actualizar_secciones")
    const btn_cerrar = document.getElementById("cerrar_dialogo")

    const formulario_actualizar = document.getElementById("formulario_actualizar_seccion")
    const input_seccion_oculto = document.getElementById("secciones_seleccionado")
    const select_actualizar_nucleo = document.getElementById("actualizar_nucleo_registrado")
    const select_actualizar_pnf = document.getElementById("actualizar_pnf_registrado")
    const select_actualizar_trayecto = document.getElementById("actualizar_trayecto_registrado")
    const select_actualizar_aula = document.getElementById("actualizar_aula_registrado")
    const select_actualizar_turno = document.getElementById("actualizar_turno_registrado")
    const input_actualizar_seccion = document.getElementById("actualizar_seccion_registrado")
  
    let filas = "", nucleo = "", pnf = "", nombre_pnf = "", periodo_academico = "", trayecto = "", aula = "", turno = "";
    let turnos = ["Diurno", "Nocturno", "Fin de Semana"];

    function getCookie(nombre) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(nombre + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(nombre.length + 1)
                    );
                    break;
                }
            }
        }

        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    /* DATOS A SELECT */

    async function nucleos_registrado() {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();
            select_registrar_nucleo.innerHTML = "<option value=''>Seleccionar el Núcleo</option>"

            resultado.nucleos.forEach(nucleo => {
                const option_nucleo_registrar = document.createElement("option")
                option_nucleo_registrar.value = nucleo.id_nucleo
                option_nucleo_registrar.textContent = nucleo.municipio
                select_registrar_nucleo.append(option_nucleo_registrar)
            }); 
        } catch (error) {
            console.error(error)
        }
    }
    nucleos_registrado();

    async function pnfs_registrados() {
        try {
            const formulario = new FormData()
            formulario.append("nucleo", nucleo)
            
            const respuesta = await fetch("/pnfs_pertenece_nucleo/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            select_registrar_pnf.innerHTML = "<option value=''>Seleccionar el P.N.F</option>"

            resultado.pnfs.forEach(pnf => {
                const option_pnf_registrar = document.createElement("option")
                option_pnf_registrar.value = pnf.id_pnf
                option_pnf_registrar.textContent = pnf.pnf
                option_pnf_registrar.dataset.periodo_academico = pnf.periodo_academico;
                select_registrar_pnf.append(option_pnf_registrar)
            }); 
        } catch (error) {
            console.error(error)
        }
    }

    async function trayectos_registrados() {
        try {
            const respuesta = await fetch("/trayectos_registrados/");
            const resultado = await respuesta.json();

            select_registrar_trayecto.innerHTML = "<option value=''>Seleccionar el Trayecto</option>";
        
            resultado.trayectos.forEach(trayecto => {
                if (nombre_pnf.toLowerCase().includes("veterinaria")) {
                    agregar_trayecto(trayecto);
                } else {
                    if (trayecto.trayecto.toLowerCase() !== "trayecto v") {
                        agregar_trayecto(trayecto);
                    }
                }
            });
        } catch (error) {
            console.error(error);
        }
    }

    function agregar_trayecto(trayecto) {
        const option_trayecto_registrar = document.createElement("option");
        option_trayecto_registrar.value = trayecto.id_trayecto;
        option_trayecto_registrar.textContent = trayecto.trayecto;
        select_registrar_trayecto.append(option_trayecto_registrar);
    }

    async function aula_academica() {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", nucleo);

            const respuesta = await fetch("/aulas_registrados/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            select_registrar_aula.innerHTML = `<option value="">Seleccionar el Aula Académica</option>`;

            resultado.aulas.forEach(aula => {
                const option_registrar = document.createElement("option");
                option_registrar.value = aula.id_aula;
                option_registrar.textContent = aula.nombre_aula;
                select_registrar_aula.append(option_registrar);
            });
        } catch (error) {
            console.error(error);
        }
    }

    function turno_academico() {
        select_registrar_turno.innerHTML = `<option value="">Seleccionar el Turno Académico</option>`;

        turnos.forEach(turno => {
            const option_registrar = document.createElement("option");
            option_registrar.value = turno;
            option_registrar.textContent = turno;
            select_registrar_turno.append(option_registrar);
        });
    }

    select_registrar_nucleo.addEventListener("change", async () => {
        nucleo = select_registrar_nucleo.value;

        await pnfs_registrados();
    });
    
    select_registrar_pnf.addEventListener("change", async (e) => {
        const opcion_seleccionada = select_registrar_pnf.options[select_registrar_pnf.selectedIndex];

        pnf = select_registrar_pnf.value;
        nombre_pnf = opcion_seleccionada.textContent
        periodo_academico = opcion_seleccionada.dataset.periodo_academico;

        await trayectos_registrados();
    });

    select_registrar_trayecto.addEventListener("change", async () => {
        trayecto = select_registrar_trayecto.value;

        await aula_academica();
    });
    
    select_registrar_aula.addEventListener("change", () => {
        aula = select_registrar_aula.value;

        turno_academico();
    });
    
    /* MOSTRAR SECCIONES ACADÉMICAS */

    async function secciones_registradas() {
        try {
            const respuesta = await fetch("/secciones_registradas/");
            const resultado = await respuesta.json();


            contenedor_secciones.innerHTML = "";

            let filas = ""; 

            resultado.secciones.forEach((seccion, index) => {
                filas += `
                    <tr data-id-seccion="${seccion.id_seccion}">
                        <td>${index + 1}</td>
                        <td>${seccion.seccion}</td>
                        <td>${seccion.id_nucleo__municipio}</td>
                        <td>${seccion.id_pnf__pnf}</td>
                        <td>${seccion.id_trayecto__trayecto}</td>
                        <td>${seccion.turno}</td>
                        <td>${seccion.id_aula__nombre_aula}</td>
                    </tr>
                `;
            });

            contenedor_secciones.innerHTML = `
                <table class="tabla_secciones">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Sección</th>
                            <th>Núcleo</th>
                            <th>PNF</th>
                            <th>Trayecto</th>
                            <th>Turno</th>
                            <th>Aula</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filas}
                    </tbody>
                </table>
            `;
        } catch(error){
            console.error("Error al registrar u obtener las secciones en la tabla:", error);
        }
    }


    secciones_registradas();

    /* FORMULARIOS */

    contenedor_secciones.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr");
        if (!fila || !fila.dataset.idSeccion) return;

        try {
            const formulario = new FormData();
            formulario.append("seccion", fila.dataset.idSeccion);

            const respuesta = await fetch("/datos_seccion/", {
                method: "POST",
                headers: { "X-CSRFToken": csrftoken },
                body: formulario
            });
            const resultado = await respuesta.json();
            const seccion = resultado.seccion;

            select_actualizar_nucleo.innerHTML = "";
            select_actualizar_pnf.innerHTML = "";
            select_actualizar_trayecto.innerHTML = "";
            select_actualizar_aula.innerHTML = "";
            select_actualizar_turno.innerHTML = "";

            input_seccion_oculto.value = seccion.id_seccion;
            input_actualizar_seccion.value = seccion.seccion;

            const crearOptionDefault = (val, txt) => {
                const opt = document.createElement("option");
                opt.value = val; opt.textContent = txt; 
                opt.selected = true; 
                opt.hidden = true;
                return opt;
            };

            select_actualizar_nucleo.append(crearOptionDefault(seccion.nucleo.id, seccion.nucleo.nombre));
            select_actualizar_pnf.append(crearOptionDefault(seccion.pnf.id, seccion.pnf.nombre));
            select_actualizar_trayecto.append(crearOptionDefault(seccion.trayecto.id, seccion.trayecto.nombre));
            select_actualizar_aula.append(crearOptionDefault(seccion.aula.id, seccion.aula.nombre));
            select_actualizar_turno.append(crearOptionDefault(seccion.turno, seccion.turno));

            await Promise.all([
                cargarNucleosActualizar(seccion.nucleo.id),
                cargarPnfsPorNucleo(seccion.nucleo.id, seccion.pnf.id),
                cargarTrayectosConValidacion(seccion.pnf.nombre, seccion.trayecto.id),
                cargarAulasPorNucleo(seccion.nucleo.id, seccion.aula.id),
                cargarTurnosActualizar(seccion.turno)
            ]);
           
            dialogo_actualizar.showModal();
        } catch (error) {
            console.error("Error general en el contenedor de secciones:", error);
        }
    });

    btn_cerrar.addEventListener("click", () => {
        dialogo_actualizar.close();
    });

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)

            const respuesta = await fetch("/modulo_seccion/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado)

            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

                await secciones_registradas();
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_registrar.reset();
        } catch (error) {
            console.error(error)
        }
    }); 

    async function cargarPnfsPorNucleo(idNucleo, pnfActualId = null) {
        try {
            const formulario = new FormData();
            formulario.append("nucleo", idNucleo);
            
            const respuesta = await fetch("/pnfs_pertenece_nucleo/", {
                method: "POST",
                headers: { "X-CSRFToken": csrftoken },
                body: formulario
            });
            const resultado = await respuesta.json();

            if (!pnfActualId) {
                select_actualizar_pnf.innerHTML = "<option value=''>Seleccionar PNF</option>";
            }

            resultado.pnfs.forEach(pnf => {
                if (pnf.id_pnf === pnfActualId) return; 
                const option = document.createElement("option");
                option.value = pnf.id_pnf;
                option.textContent = pnf.pnf;
                option.dataset.periodo_academico = pnf.periodo_academico;
                select_actualizar_pnf.append(option);
            });
        } catch (error) {
            console.error("Error al cargar los PNFs:", error);
        }
    }

    async function cargarTrayectosConValidacion(nombrePnfActual, trayectoActualId = null) {
        try {
            const respuesta = await fetch("/trayectos_registrados/");
            const resultado = await respuesta.json();

            resultado.trayectos.forEach(trayecto => {
                if (trayecto.id_trayecto === trayectoActualId) return; 

                const esVeterinaria = nombrePnfActual.toLowerCase().includes("PNF en Medicina Veterinaria");
                const esTrayectoV = trayecto.trayecto.toLowerCase() === "trayecto v";

                if (esVeterinaria || !esTrayectoV) {
                    const option = document.createElement("option");
                    option.value = trayecto.id_trayecto;
                    option.textContent = trayecto.trayecto;
                    select_actualizar_trayecto.append(option);
                }
            });
        } catch (error) {
            console.error("Error al cargar trayectos:", error);
        }
    }

    async function cargarAulasPorNucleo(idNucleo, aulaActualId = null) {
        try {
            const formulario = new FormData();
            formulario.append("id_nucleo", idNucleo);

            const respuesta = await fetch("/aulas_registrados/", {
                method: "POST",
                headers: { "X-CSRFToken": csrftoken },
                body: formulario
            });
            const resultado = await respuesta.json();

            resultado.aulas.forEach(aula => {
                if (aula.id_aula === aulaActualId) return; 

                const option = document.createElement("option");
                option.value = aula.id_aula;
                option.textContent = aula.nombre_aula;
                select_actualizar_aula.append(option);
            });
        } catch (error) {
            console.error("Error al cargar las aulas:", error);
        }
    }

    async function cargarNucleosActualizar(nucleoActualId = null) {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();

            resultado.nucleos.forEach(nucleo => {
                if (nucleo.id_nucleo === nucleoActualId) return;

                const option = document.createElement("option");
                option.value = nucleo.id_nucleo;
                option.textContent = nucleo.municipio; 
                select_actualizar_nucleo.append(option);
            });           
        } catch (error) {
            console.error("Error al cargar núcleos:", error);
        }
    }

    function cargarTurnosActualizar(turnoActual = null) {
        turnos.forEach(turno => {
            if (turno === turnoActual) return;

            const option = document.createElement("option");
            option.value = turno;
            option.textContent = turno;
            select_actualizar_turno.append(option);
        });
    }

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar)

            const respuesta = await fetch("/guardar_actualizacion_seccion/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            dialogo_actualizar.close();
            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });

                await secciones_registradas();
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
        } catch (error) {
            console.error(error)
        }
    });
});