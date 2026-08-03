document.addEventListener("DOMContentLoaded", () => {

    const contenedor_secciones = document.getElementById("contenedor_secciones");
    const dialogo_actualizar = document.getElementById("dialogo_actualizar_secciones");
    const btn_cerrar = document.getElementById("cerrar_dialogo");

    const formulario_actualizar = document.getElementById("formulario_actualizar_seccion");
    
    const input_seccion_oculto = document.getElementById("secciones_seleccionado");
    const select_actualizar_pnf = document.getElementById("actualizar_pnf_registrado");
    const select_actualizar_trayecto = document.getElementById("actualizar_trayecto_registrado");
    const select_actualizar_aula = document.getElementById("actualizar_aula_registrado");
    const select_actualizar_turno = document.getElementById("actualizar_turno_registrado");
    const input_actualizar_seccion = document.getElementById("actualizar_seccion_registrado");
    
    const mensaje_actualizar_seccion = document.getElementById("mensaje_actualizar_seccion");

    const btn_actualizar = document.getElementById("btn_actualizar");
  
    let filas = "", nucleo = "", pnf = "", nombre_pnf = "", periodo_academico = "", trayecto = "", aula = "", turno = "";
    let turnos = ["Diurno", "Nocturno", "Fin de Semana"];

    async function secciones_registradas() {
        try {
            const respuesta = await fetch("/sec_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            contenedor_secciones.innerHTML = "";
            resultado.secciones.forEach((seccion, index) => {
                filas += `
                    <tr data-id-seccion="${seccion.id_seccion}">
                        <td>${index + 1}</td>
                        <td>${seccion.id_pnf__pnf}</td>
                        <td>${seccion.id_aula__nombre_aula}</td>
                        <td>${seccion.trayecto}</td>
                        <td>${seccion.turno}</td>
                        <td>${seccion.seccion}</td>
                    </tr>
                `;
            });

            contenedor_secciones.innerHTML = filas;
        } catch(error){
            console.error(error);
            
        }
    }
    secciones_registradas();

    async function pnfs_registrados() {
        try {
            const respuesta = await fetch("/pnfs_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_actualizar_pnf.innerHTML = "";
            resultado.nucleos.forEach(nucleo => {
                nucleo.pnfs.forEach(pnf => {
                    const option = document.createElement("option");
                    option.value = pnf.id_pnf;
                    option.textContent = pnf.pnf;
                    select_actualizar_pnf.appendChild(option);
                });
            });
        } catch (error) {
            console.error(error);
        }
    }
    pnfs_registrados();

    async function aula_academica() {
        try {
            const respuesta = await fetch("/aulas_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_actualizar_aula.innerHTML = "";
            resultado.aulas.forEach(aula => {
                const option_registrar = document.createElement("option");
                option_registrar.value = aula.id_aula;
                option_registrar.textContent = aula.nombre_aula;
                select_actualizar_aula.append(option_registrar);
            });
        } catch (error) {
            console.error(error);
        }
    }
    aula_academica();

    async function validar_seccion() {
        try {
            const formulario = new FormData();
            formulario.append("id_seccion", input_seccion_oculto.value);
            formulario.append("seccion", input_actualizar_seccion.value);

            const respuesta = await fetch("/val_sec/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.existe) {
                input_actualizar_seccion.setCustomValidity("Ya existe un pnf con el mismo nombre.");
                input_actualizar_seccion.classList.add("is-invalid");
                input_actualizar_seccion.classList.remove("is-valid");

                mensaje_actualizar_seccion.textContent = "Ya existe un pnf con el mismo nombre.";
                mensaje_actualizar_seccion.style.color = "#dc3545";

                btn_actualizar.disabled = true;
            } else {
                input_actualizar_seccion.setCustomValidity("");
                input_actualizar_seccion.classList.add("is-valid");
                input_actualizar_seccion.classList.remove("is-invalid");

                mensaje_actualizar_seccion.textContent = "El nombre del PNF está disponible.";
                mensaje_actualizar_seccion.style.color = "#198754";

                btn_actualizar.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_actualizar_seccion.addEventListener("input", async () => {
        await validar_seccion();
    });

    input_actualizar_seccion.addEventListener("paste", async () => {
        await validar_seccion();
    });

    contenedor_secciones.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr");
        if (!fila) return;

        try {
            const formulario = new FormData();
            formulario.append("seccion", fila.dataset.idSeccion);

            const respuesta = await fetch("/datos_sec/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            dialogo_actualizar.showModal();
         
            input_seccion_oculto.value = resultado.seccion.id_seccion;
            input_actualizar_seccion.value = resultado.seccion.seccion;
            
            const option_pnf = document.createElement("option");
            option_pnf.value = resultado.seccion.pnf.id;
            option_pnf.textContent = resultado.seccion.pnf.nombre;
            option_pnf.selected = true;
            option_pnf.hidden = true;
            select_actualizar_pnf.append(option_pnf);
            
            const option_aula = document.createElement("option");
            option_aula.value = resultado.seccion.aula.id;
            option_aula.textContent = resultado.seccion.aula.nombre;
            option_aula.selected = true;
            option_aula.hidden = true;
            select_actualizar_aula.append(option_aula);
            
            const option_trayecto = document.createElement("option");
            option_trayecto.value = resultado.seccion.trayecto;
            option_trayecto.textContent = resultado.seccion.trayecto;
            option_trayecto.selected = true;
            option_trayecto.hidden = true;
            select_actualizar_trayecto.append(option_trayecto);
            
            select_actualizar_turno.innerHTML = "";

            const option_turno = document.createElement("option");
            option_turno.value = resultado.seccion.turno;
            option_turno.textContent = resultado.seccion.turno;
            option_turno.selected = true;
            option_turno.hidden = true;
            select_actualizar_turno.append(option_turno);

            turnos.forEach(turno => {
                if (turno !== resultado.seccion.turno) {
                    const option = document.createElement("option");
                    option.value = turno;
                    option.textContent = turno;
                    select_actualizar_turno.append(option);
                }
            });

        } catch (error) {
            console.error(error);
        }
    });

    select_actualizar_turno.addEventListener("change", async () => {
        try {
            const formulario = new FormData();
            formulario.append("id_seccion", input_seccion_oculto.value);
            formulario.append("turno", select_actualizar_turno.value);

            const respuesta = await fetch("/turno_sec/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            dialogo_actualizar.close();

            if (!resultado.existe) {
                const alerta = await Swal.fire({
                    icon: "question",
                    title: "Turno disponible",
                    text: `El turno ${select_actualizar_turno.value} está disponible. ¿Desea actualizar la sección con este turno?`,
                    showCancelButton: true,
                    confirmButtonText: "Sí, actualizar",
                    cancelButtonText: "Cancelar"
                });

                if (!alerta.isConfirmed) {
                    return;
                }

                const formulario = new FormData();
                formulario.append("id_actual", input_seccion_oculto.value);
                formulario.append("turno", select_actualizar_turno.value);

                const respuesta = await fetch("/act_turno/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: formulario
                });
                const resultado_actualizar = await respuesta.json();

                await Swal.fire({
                    icon: resultado_actualizar.icon,
                    title: resultado_actualizar.title,
                    text: resultado_actualizar.descripcion
                });

                filas = "";
                await secciones_registradas();
                return;
            }   

            const alerta = await Swal.fire({
                icon: "warning",
                title: "Turno ocupado",
                html: `
                    El turno <b>${resultado.seccion.turno}</b> ya pertenece a la sección
                    <b>${resultado.seccion.seccion}</b>.<br><br>
                    ¿Desea intercambiar los turnos?
                `,
                showDenyButton: true,
                showCancelButton: true,
                confirmButtonText: "Intercambiar",
                denyButtonText: "No",
                cancelButtonText: "Cancelar"
            });

            if (alerta.isConfirmed) {
                const datos = new FormData();
                datos.append("accion", "intercambio");
                datos.append("id_actual", input_seccion_oculto.value);
                datos.append("turno_nuevo", select_actualizar_turno.value);
                datos.append("id_otro", resultado.seccion.id);
                datos.append("turno_otro", resultado.seccion.turno);

                const respuesta_actualizar = await fetch("/act_turno/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: datos
                });
                const resultado_actualizar = await respuesta_actualizar.json();

                await Swal.fire({
                    icon: resultado_actualizar.icon,
                    title: resultado_actualizar.title,
                    text: resultado_actualizar.descripcion
                });

                filas = "";
                await secciones_registradas();
            }
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
            const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/guardar_act_sec/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            dialogo_actualizar.close();

            filas = "";
            await secciones_registradas();

            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        } catch (error) {
            console.error(error);
        }
    });

});