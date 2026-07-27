document.addEventListener("DOMContentLoaded", () => {

    const input_cantida_Fila = document.getElementById("cantidad_fila");
    const contenedorHorario = document.getElementById("contenedor_horario");
    const btn_generar_pnf = document.getElementById("generar_pdf")
    
    const formulario_registrar = document.getElementById("formulario_registrar_horario")
    
    const select_nucelos_registrado = document.getElementById("nucelos_registrados")
    const select_pnfs_registrado = document.getElementById("pnfs_registrados")
    const select_trayectos_registrado = document.getElementById("trayectos_registrados")
    const select_periodos_academicas_registrado = document.getElementById("periodos_academicas_registrados")
    const select_aulas_registrado = document.getElementById("aulas_registrados")
    const select_turno_academica = document.getElementById("turno_academica")

    let pnf = "", trayecto = "", periodo = "", nucleo = "", nombre_pnf = "", aula = "";
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

    async function nucleos_registrado() {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();

            select_nucelos_registrado.innerHTML = "<option value=''>Seleccionar el Núcleo</option>"

            resultado.nucleos.forEach(nucleo => {
                const option_nucleo_registrar = document.createElement("option")
                option_nucleo_registrar.value = nucleo.id_nucleo
                option_nucleo_registrar.textContent = nucleo.municipio
                select_nucelos_registrado.append(option_nucleo_registrar)
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

            select_pnfs_registrado.innerHTML = "<option value=''>Seleccionar el P.N.F</option>"

            resultado.pnfs.forEach(pnf => {
                const option_pnf_registrar = document.createElement("option")
                option_pnf_registrar.value = pnf.id_pnf
                option_pnf_registrar.textContent = pnf.pnf
                option_pnf_registrar.dataset.periodo_academico = pnf.periodo_academico;
                select_pnfs_registrado.append(option_pnf_registrar)
            }); 
        } catch (error) {
            console.error(error)
        }
    }

    async function trayectos_registrados() {
        try {
            const respuesta = await fetch("/trayectos_registrados/");
            const resultado = await respuesta.json();

            select_trayectos_registrado.innerHTML = "<option value=''>Seleccionar el Trayecto</option>";
        
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
        select_trayectos_registrado.append(option_trayecto_registrar);
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

            select_aulas_registrado.innerHTML = `<option value="">Seleccionar el Aula Académica</option>`;

            resultado.aulas.forEach(aula => {
                const option_registrar = document.createElement("option");
                option_registrar.value = aula.id_aula;
                option_registrar.textContent = aula.nombre_aula;
                select_aulas_registrado.append(option_registrar);
            });
        } catch (error) {
            console.error(error);
        }
    }

    function turno_academico() {
        select_turno_academica.innerHTML = `<option value="">Seleccionar el Turno Académico</option>`;

        turnos.forEach(turno => {
            const option_registrar = document.createElement("option");
            option_registrar.value = turno;
            option_registrar.textContent = turno;
            select_turno_academica.append(option_registrar);
        });
    }

    async function periodo_academico() {
         try {
            const respuesta = await fetch("/periodos_academicos/");
            const resultado = await respuesta.json();

            select_periodos_academicas_registrado.innerHTML = `<option value="">Seleccionar el Periodo Académico</option>`;

            resultado.periodos.forEach(periodo => {
                const option_registrar = document.createElement("option");
                option_registrar.value = periodo.id_periodo_academico;
                option_registrar.textContent = periodo.nombre;
                select_periodos_academicas_registrado.append(option_registrar);
            });
        } catch (error) {
            console.error(error);
        }
    }
    periodo_academico();

    select_nucelos_registrado.addEventListener("change", async () => {
        nucleo = select_nucelos_registrado.value;

        await pnfs_registrados();
        await datos_busqueda();
    });
    
    select_pnfs_registrado.addEventListener("change", async (e) => {
        const opcion_seleccionada = select_pnfs_registrado.options[select_pnfs_registrado.selectedIndex];

        pnf = select_pnfs_registrado.value;
        nombre_pnf = opcion_seleccionada.textContent
        periodo_academico = opcion_seleccionada.dataset.periodo_academico;

        await trayectos_registrados();
        await datos_busqueda()
    });

    select_trayectos_registrado.addEventListener("change", async () => {
        trayecto = select_trayectos_registrado.value;

        await aula_academica();
        await datos_busqueda()
    });
    
    select_periodos_academicas_registrado.addEventListener("change", async () => {
        periodo = select_periodos_academicas_registrado.value;
    });

    select_aulas_registrado.addEventListener("change", () => {
        aula = select_aulas_registrado.value;

        turno_academico();
    });

    async function datos_busqueda() {
        if (pnf && trayecto && nucleo) {
            cargarMaterias();
        }
    }

    let materias = [];
    async function cargarMaterias() {
        if (!pnf || !trayecto || !nucleo) return;

        const formulario = new FormData();

        formulario.append("nucleos", nucleo);
        formulario.append("pnfs", pnf);
        formulario.append("trayecto", trayecto);

        const respuesta = await fetch("/buscar_materias_docente/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            },
            body: formulario
        });

        const resultado = await respuesta.json();
        console.log(resultado);

        if (resultado.success) {
            materias = resultado.materias;
        } else {
            materias = [];
        }
    }

    input_cantida_Fila.addEventListener("keydown", (e) => {
        const teclasPermitidas = [
            "Backspace",
            "Delete",
            "Tab",
            "ArrowLeft",
            "ArrowRight",
            "Home",
            "End"
        ];
        if (teclasPermitidas.includes(e.key)) {
            return;
        }
        if (!/^[1-8]$/.test(e.key)) {
            e.preventDefault();
        }
    });
  
    input_cantida_Fila.addEventListener("input", () => {

        input_cantida_Fila.value = input_cantida_Fila.value.replace(/\D/g, "");
        let cantidad = parseInt(input_cantida_Fila.value);

        if (input_cantida_Fila.value.length > 1) {
            input_cantida_Fila.value = input_cantida_Fila.value.charAt(0);
        }

        if (isNaN(cantidad)) {
            contenedorHorario.innerHTML = "";
            return;
        }

        if (cantidad > 8) {
            cantidad = 8;
            input_cantida_Fila.value = 8;
        }

        contenedorHorario.innerHTML = "";

        for (let i = 0; i < cantidad; i++) {
            const fila = document.createElement("tr");

            const tdInicio = document.createElement("td");
            const inputInicio = document.createElement("input");
            inputInicio.type = "time";
            inputInicio.required = true;
            tdInicio.appendChild(inputInicio);
            fila.appendChild(tdInicio);

            const tdFinal = document.createElement("td");
            const inputFinal = document.createElement("input");
            inputFinal.type = "time";
            inputFinal.required = true;
            tdFinal.appendChild(inputFinal);
            fila.appendChild(tdFinal);

            for (let j = 0; j < 5; j++) {
                const td = document.createElement("td");

                const selectMateria = document.createElement("select");
                selectMateria.required = true;

                const opcionInicial = document.createElement("option");
                opcionInicial.value = "";
                opcionInicial.textContent = "Seleccione";
                opcionInicial.selected = true;
                opcionInicial.disabled = true;
                selectMateria.appendChild(opcionInicial);

                materias.forEach(materia => {
                    const option = document.createElement("option");
                    option.value = materia.id_materia;
                    option.textContent = `${materia.materia} - ${materia.docente}`;
                    selectMateria.appendChild(option);
                });

                td.appendChild(selectMateria);
                fila.appendChild(td);
            }

            contenedorHorario.appendChild(fila);
        }
    });


    function obtenerHorario() {
        const horario = [];
        document.querySelectorAll("#contenedor_horario tr").forEach(fila => {
            const inputs = fila.querySelectorAll("input");
            const selects = fila.querySelectorAll("select");

            if (inputs.length < 2 || selects.length < 5) {
                return;
            }

            horario.push({
                hora_inicio: inputs[0].value,
                hora_final: inputs[1].value,

                lunes: selects[0].value || "",
                martes: selects[1].value || "",
                miercoles: selects[2].value || "",
                jueves: selects[3].value || "",
                viernes: selects[4].value || ""
            });
        });
        return horario;
    }

    async function generarPDF(horario) {
        const formulario = new FormData(formulario_registrar);
        const datos = {
            nucleos: formulario.get("nucleos"),
            pnfs: formulario.get("pnfs"),
            trayecto: formulario.get("trayecto"),
            periodo: formulario.get("periodo"),
            aulas: formulario.get("aulas"),
            turno: formulario.get("turno"),
            horario: horario
        };

        const respuesta = await fetch("/generar_horario_pdf/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(datos)
        });

        if (!respuesta.ok) {
            const error = await respuesta.json();
            return;
        }

        const blob = await respuesta.blob();
        const url = window.URL.createObjectURL(blob);
        const enlace = document.createElement("a");

        enlace.href = url;
        enlace.download = "Horario_Academico.pdf";

        document.body.appendChild(enlace);
        enlace.click();
        enlace.remove();
        window.URL.revokeObjectURL(url);
    }

    btn_generar_pnf.addEventListener("click", async function (e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);
            const respuesta = await fetch("/modulo_horario_academico/", {
                method: "POST",
                body: formulario
            });

            const resultado = await respuesta.json();
            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado !== "ok") {
                return;
            }

            const horario = obtenerHorario();

            if (horario.length === 0) {
                Swal.fire({
                    icon: "warning",
                    text: "No existen datos del horario para generar el PDF."
                });
                return;
            }
            
            await generarPDF(horario);

            formulario_registrar.reset();
        } catch (error) {
            console.error("Error:", error);
        }
    });
});