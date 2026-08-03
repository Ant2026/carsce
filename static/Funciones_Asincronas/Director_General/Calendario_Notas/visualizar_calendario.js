document.addEventListener("DOMContentLoaded", () => {

    const formulario_actualizar = document.getElementById("actualizar_calendario");
    const contenedor_calendario_academico = document.getElementById("contenedor_registrado");

    const input_actualizar_fecha_Inicial = document.getElementById("fecha_inicial_academica");
    const input_actualizar_fecha_final = document.getElementById("fecha_final_academica");
    const input_oculto_actualizar = document.getElementById("fecha_seleccionado");

    const dialogo_actualizar = document.getElementById("dialogo_actualizar_calendario");
    const btn_cerrar = document.getElementById("cerrar_dialogo");

    async function cargarCalendarios() {
        const response = await fetch("/calendarios_lista/");
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

            const respuesta = await fetch("/calendario_datos/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
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
            input_actualizar_fecha_Inicial.value = resultado.calendario.inicio;
            input_actualizar_fecha_final.value = resultado.calendario.final;

            limitarMes(
                input_actualizar_fecha_Inicial,
                resultado.calendario.inicio
            );

            limitarMes(
                input_actualizar_fecha_final,
                resultado.calendario.inicio
            );
        } catch (error) {
            console.error(error)
        }
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/calendario_guardar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
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

    btn_cerrar.addEventListener("click", () => {
        dialogo_actualizar.close();
    });
});