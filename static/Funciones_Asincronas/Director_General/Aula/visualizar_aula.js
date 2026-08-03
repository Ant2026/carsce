document.addEventListener("DOMContentLoaded", () => {

    const formulario_actualizar = document.getElementById("formulario_actualizar_aula");
    const contenedor_aulas = document.getElementById("contenedor_aulas");
    
    const dialogo_actualizar_aula = document.getElementById("dialogo_actualizar_aula");

    const input_id_aula_oculto = document.getElementById("aula_seleccionar");
    const input_aula_actualizar = document.getElementById("actualizar_nombre_aula");
    const input_edificio_actualizar = document.getElementById("actualizar_nombre_edificio");
    const input_piso_actualizar = document.getElementById("actualizar_piso_edificio");
    const select_nucleo_actualizar = document.getElementById("actualizar_nucleo_aula");

    const btn_cerrar_actualizar = document.getElementById("cerrar_dialogo");

    async function aulas_registradas() {
        try {
            const respuesta = await fetch("/aulas_reg/");
            const resultado = await respuesta.json();

            let filas = "";
            Object.entries(resultado).forEach(([municipio, aulas]) => {
                aulas.forEach((aula, index) => {
                    filas += `
                        <tr data-id="${aula.id_aula}">

                            <td>${index + 1}</td>
                            <td>${aula.nombre_aula}</td>
                            <td>${aula.nombre_edificio}</td>
                            <td>${aula.piso_edificio}</td>
                        </tr>
                    `;
                });
            });

            contenedor_aulas.innerHTML = filas;
        } catch (error) {
            console.error(error);
        }
    }
    aulas_registradas();

    contenedor_aulas.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr");
        if (!fila) return;

        try {
            const formulario = new FormData();
            formulario.append("id_aula", fila.dataset.id);

            const respuesta = await fetch("/datos_a/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            dialogo_actualizar_aula.showModal();

            if (resultado.estado === "fallo") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    title: resultado.title,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                return;
            }

            input_id_aula_oculto.value = resultado.id_aula;
            input_aula_actualizar.value = resultado.nombre_aula;
            input_edificio_actualizar.value = resultado.nombre_edificio;
            input_piso_actualizar.value = resultado.piso_edificio;
        } catch (error) {
            console.error(error)
        }
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/act_aula_acad/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            dialogo_actualizar_aula.close();
            
            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                await aulas_registradas();
            }
        } catch (error) {
            console.error(error);
        }
    });

    btn_cerrar_actualizar.addEventListener("click", () => {
        dialogo_actualizar_aula.close()
    });
});