document.addEventListener("DOMContentLoaded", () => {

    const formulario_buscar = document.getElementById("buscar_materia");
    const formulario_actualizar = document.getElementById("actualizar_materia");

    const codigos_buscar_materias = document.getElementById("codigos_buscar_materias");

    const input_materia_oculta = document.getElementById("materia_seleccionado");
    const input_actualizar_nombre = document.getElementById("nombres_actualizar_materias");
    const select_actualizar_recuperacion = document.getElementById("reparacion_actualizar_materia");
    const select_actualizar_pnf = document.getElementById("pnfs_actualizar_materia");

    const btn_registrar = document.getElementById("btn_registrar");

    async function pnfs_registrados() {
        try {
            const respuesta = await fetch("/pnfs_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            resultado.nucleos.forEach(nucleo => {
                nucleo.pnfs.forEach(pnf => {
                    const option = document.createElement("option");
                    option.value = pnf.id_pnf;
                    option.textContent = pnf.pnf;
                    select_actualizar_pnf.appendChild(option);
                });
            });
        } catch (error) {
            console.error(error)
        }
    }
    pnfs_registrados();

    controles = [
        input_actualizar_nombre,
        select_actualizar_recuperacion,
        select_actualizar_pnf,
        btn_registrar
    ]

    function bloquear_controles(controles, estado) {
        controles.forEach(control => control.disabled = estado);
    }

    bloquear_controles(controles, true);

    formulario_buscar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_buscar);
            const respuesta = await fetch("/mat_datos/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            formulario_buscar.reset();
            if (resultado.estado == "fallo") {
                await Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    title: resultado.title,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                return;
            }

            bloquear_controles(controles, false);

            input_materia_oculta.value = resultado.materia.id_materia;
            input_actualizar_nombre.value = resultado.materia.nombre;

            const option_reparacion = document.createElement("option");
            option_reparacion.value = resultado.materia.recuperacion;
            option_reparacion.textContent = resultado.materia.recuperacion;
            option_reparacion.selected = true;
            option_reparacion.hidden = true;
            select_actualizar_recuperacion.append(option_reparacion);

            const option_pnf = document.createElement("option");
            option_pnf.value = resultado.pnf.id_pnf;
            option_pnf.textContent = resultado.pnf.pnf;
            option_pnf.selected = true;
            option_pnf.hidden = true;
            select_actualizar_pnf.append(option_pnf);

        } catch (error) {
            console.error(error)
        }
    });
    
    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar)
            const respuesta = await fetch("/mat_guardar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json()
            console.log(resultado);

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_actualizar.reset();
                bloquear_controles(controles, true);
            }
        } catch (error) {
            console.error(error)
        }
    });

    codigos_buscar_materias.addEventListener("input", function () {
        this.value = this.value
            .toUpperCase()
            .replace(/[^A-Z0-9]/g, "")
            .slice(0, 7); 
    });
});