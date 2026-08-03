document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registrar");
    
    const select_registrar_pnf = document.getElementById("registro_pnf");
    const select_registrar_trayecto = document.getElementById("registro_trayecto");
    const select_registrar_aula = document.getElementById("registro_aula");
    const select_registrar_turno = document.getElementById("registro_turno");
    const input_registrar_seccion = document.getElementById("registro_seccion");

    const mensaje_nombre_seccion = document.getElementById("mensaje_nombre_seccion");
    const mensaje_aula_academica = document.getElementById("mensaje_aula_academica");

    const btn_registro = document.getElementById("btn_registro");

    let turnos = ["Diurno", "Nocturno", "Fin de Semana"];

    async function validar_seccion() {
        try {
            const formulario = new FormData();
            formulario.append("seccion", input_registrar_seccion.value);

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
                input_registrar_seccion.setCustomValidity("Ya existe un pnf con el mismo nombre.");
                input_registrar_seccion.classList.add("is-invalid");
                input_registrar_seccion.classList.remove("is-valid");

                mensaje_nombre_seccion.textContent = "Ya existe un pnf con el mismo nombre.";
                mensaje_nombre_seccion.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                input_registrar_seccion.setCustomValidity("");
                input_registrar_seccion.classList.add("is-valid");
                input_registrar_seccion.classList.remove("is-invalid");

                mensaje_nombre_seccion.textContent = "El nombre del PNF está disponible.";
                mensaje_nombre_seccion.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_registrar_seccion.addEventListener("input", async () => {
        await validar_seccion();
    });

    input_registrar_seccion.addEventListener("paste", async () => {
        await validar_seccion();
    });

    select_registrar_aula.addEventListener("change", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData();
            formulario.append("aula", select_registrar_aula.value);

            const respuesta = await fetch("/bus_aula/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            const turnosOcupados = resultado.secciones.map(seccion => seccion.turno);

            select_registrar_turno.innerHTML = "<option value='' selected>Seleccionar el Turno Académico</option>";

            mensaje_aula_academica.textContent = "";
            
            turnos.forEach(turno => {
                if (!turnosOcupados.includes(turno)) {
                    const option = document.createElement("option");
                    option.value = turno;
                    option.textContent = turno;
                    select_registrar_turno.appendChild(option);
                }
            });

            if (select_registrar_turno.options.length === 1) {
                mensaje_aula_academica.textContent = "Esta aula ya tiene asignados todos los turnos académicos.";
                btn_registro.disabled = true;
            }
        } catch (error) {
            console.error(error);
        }
    });

    async function pnfs_registrados() {
        try {
            const respuesta = await fetch("/pnfs_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_registrar_pnf.innerHTML = "<option value='' selected>Seleccionar el P.N.F</option>";

            resultado.nucleos.forEach(nucleo => {
                nucleo.pnfs.forEach(pnf => {
                    const option = document.createElement("option");
                    option.value = pnf.id_pnf;
                    option.textContent = pnf.pnf;
                    select_registrar_pnf.appendChild(option);
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

            select_registrar_aula.innerHTML = "<option value='' selected>Seleccionar el Aula Académica</option>";

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
    aula_academica();

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/reg_sec/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_registrar.reset();
            }
        } catch (error) {
            console.error(error);
        }
    }); 

});