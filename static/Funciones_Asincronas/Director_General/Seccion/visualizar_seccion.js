document.addEventListener("DOMContentLoaded", () => {

    const contenedor_secciones = document.getElementById("contenedor_secciones");
    const dialogo_actualizar = document.getElementById("dialogo_actualizar_secciones");
    const btn_cerrar = document.getElementById("cerrar_dialogo");

    const formulario_actualizar = document.getElementById("formulario_actualizar_seccion");
    
    const input_seccion_oculto = document.getElementById("secciones_seleccionado");
    const select_actualizar_turno = document.getElementById("actualizar_turno_registrado");
    const input_actualizar_seccion = document.getElementById("actualizar_seccion_registrado");
    const mensaje_actualizar_seccion = document.getElementById("mensaje_actualizar_seccion");

    const btn_actualizar = document.getElementById("btn_actualizar");
  
    let filas = "";

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
                        <td>${seccion.nombre}</td>
                        <td>${seccion.turno}</td>
                    </tr>
                `;
            });

            contenedor_secciones.innerHTML = filas;
        } catch(error){
            console.error(error);
            
        }
    }
    secciones_registradas();

    async function validar_seccion() {
        try {
            const formulario = new FormData();
            formulario.append("seccion", input_actualizar_seccion.value);
            formulario.append("id_seccion", secciones_seleccionado.value);

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
                input_actualizar_seccion.setCustomValidity("Ya existe una sección con el mismo nombre.");
                input_actualizar_seccion.classList.add("is-invalid");
                input_actualizar_seccion.classList.remove("is-valid");

                mensaje_actualizar_seccion.textContent = "Ya existe una sección con el mismo nombre.";
                mensaje_actualizar_seccion.style.color = "#dc3545";

                btn_actualizar.disabled = true;
            } else {
                input_actualizar_seccion.setCustomValidity("");
                input_actualizar_seccion.classList.add("is-valid");
                input_actualizar_seccion.classList.remove("is-invalid");

                mensaje_actualizar_seccion.textContent = "El nombre de la sección está disponible.";
                mensaje_actualizar_seccion.style.color = "#198754";

                btn_actualizar.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }
    input_actualizar_seccion.addEventListener("input", validar_seccion)

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
            
            select_actualizar_turno.innerHTML = "";

            const option_turno = document.createElement("option");
            option_turno.value = resultado.seccion.turno;
            option_turno.textContent = resultado.seccion.turno;
            option_turno.selected = true;
            option_turno.hidden = true;
            select_actualizar_turno.append(option_turno);
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