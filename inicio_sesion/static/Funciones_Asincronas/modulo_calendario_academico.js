document.addEventListener("DOMContentLoaded", () => {

    const input_date_Inicial = document.getElementById("fecha_Inicial")
    const input_date_Reparacion = document.getElementById("fecha_Reparacion")
    const input_date_TramoI = document.getElementById("fecha_TramoI")
    const input_date_TramoII = document.getElementById("fecha_TramoII")
    const input_date_TramoIII = document.getElementById("fecha_TramoIII")
    const input_date_SemestreI = document.getElementById("fecha_SemestreI")
    const input_date_SemestreII = document.getElementById("fecha_SemestreII")

    const formulario_registrar = document.getElementById("registrar_calendario")
    const formulario_actualizar = document.getElementById("actualizar_calendario")

    const contenedor_calendario_academico = document.getElementById("contenedor_registrado")

    const select_actualizar_fecha = document.getElementById("actualizar_fechaacademica")
    const input_actualizar_fecha_Inicial = document.getElementById("fecha_inicial_academica")
    const input_actualizar_fecha_final = document.getElementById("fecha_final_academica")
    const input_oculto_actualizar = document.getElementById("fecha_seleccionado")

    const dialogo_actualizar = document.getElementById("dialogo_actualizar_calendario")
    const btn_cerrar = document.getElementById("cerrar_dialogo")

    function limitarMes(input, mes) {
        const anio = new Date().getFullYear(); // Año actual
        const ultimoDia = new Date(anio, mes, 0).getDate();

        input.min = `${anio}-${String(mes).padStart(2, "0")}-01`;
        input.max = `${anio}-${String(mes).padStart(2, "0")}-${String(ultimoDia).padStart(2, "0")}`;
    }

    limitarMes(document.getElementById("fecha_Inicial"), 11);    
    limitarMes(document.getElementById("fecha_Reparacion"), 12); 
    limitarMes(document.getElementById("fecha_TramoI"), 4); 
    limitarMes(document.getElementById("fecha_TramoII"), 7);    
    limitarMes(document.getElementById("fecha_TramoIII"), 11); 
    limitarMes(document.getElementById("fecha_SemestreI"), 7); 
    limitarMes(document.getElementById("fecha_SemestreII"), 3); 

    async function cargarPeriodosAcademicos() {
        const respuesta = await fetch("/periodos_academicos/");
        const resultado = await respuesta.json();

        if (resultado.estado === "exito") {
            select_actualizar_fecha.innerHTML = '<option selected>Seleccione una opción</option>';

            resultado.periodos.forEach(periodo => {
                const option = document.createElement("option");
                option.value = periodo.id_periodo_academico;
                option.textContent = periodo.nombre;

                select_actualizar_fecha.appendChild(option);
            });
        }
    }
    cargarPeriodosAcademicos()
    
    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/modelo_calendario_academico/", {
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
            formulario_registrar.reset()
        } catch (error) {
            console.error(error)
        }
    });

    btn_cerrar.addEventListener("click", () => {
        dialogo_actualizar.close();
    });

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

    async function cargarCalendarios() {
        const response = await fetch("/calendarios_registrados/");
        const data = await response.json();
        console.log(data)

        contenedor_calendario_academico.innerHTML = "";

        if (data.estado === "exito") {
            data.calendarios.forEach(cal => {

                const fila = document.createElement("tr");

                fila.setAttribute("data-id", cal.id_fecha_academica);

                fila.innerHTML = `
                    <td>${cal.periodo__nombre}</td>
                    <td>${cal.fecha_inicio}</td>
                    <td>${cal.fecha_final}</td>
                `;

                contenedor_calendario_academico.appendChild(fila);
            });
        }
    }
    cargarCalendarios();

    contenedor_calendario_academico.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr"); 
        if (!fila) return;

        const id = fila.dataset.id; 
        try {
            const formulario = new FormData()
            formulario.append("id_calendario", id)

            const respuesta = await fetch("/datos_calendario/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()
            if (resultado.estado == "error") {
                dialogo_actualizar.close()
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            dialogo_actualizar.showModal();
            input_oculto_actualizar.value = resultado.calendario.id;
            
            select_actualizar_fecha.innerHTML = "";

            const option = document.createElement("option");
            option.value = resultado.calendario.periodo_id;
            option.textContent = resultado.calendario.periodo;
            option.selected = true;
            option.hidden = true;

            select_actualizar_fecha.appendChild(option);

            input_actualizar_fecha_Inicial.value = resultado.calendario.inicio;
            input_actualizar_fecha_final.value = resultado.calendario.final;
        } catch (error) {
            console.error(error)
        }
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/guardar_actualizar_calendario/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            dialogo_actualizar.close()
        
            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            await cargarCalendarios();
        } catch (error) {
            console.error(error);
        }
    });
});