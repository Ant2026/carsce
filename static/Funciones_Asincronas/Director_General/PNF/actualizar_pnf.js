document.addEventListener("DOMContentLoaded", async () => {

    const formulario_buscar = document.getElementById("formulario_buscar");

    const pnf_seleccionado = document.getElementById("pnf_seleccionado");
    const actualizar_nombre_pnf = document.getElementById("actualizar_nombre_pnf");
    const actualizar_periodo_academico = document.getElementById("actualizar_periodo_academico");

    const formulario_actualizar = document.getElementById("formulario_actualizar");

    const btn_actualizar = document.getElementById("btn_actualizar");

    const controles_actualizar = [
        actualizar_nombre_pnf,
        actualizar_periodo_academico,
        btn_actualizar
    ] 
 
    function bloquear_controles(controles, estado) {
        controles.forEach(control => control.disabled = estado);
    }

    bloquear_controles(controles_actualizar, true);

    formulario_buscar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_buscar);

            const respuesta = await fetch("/datos_pnf/", {
                method: "POST",
                body: formulario,
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado == "fallo") {
                Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                return;
            }

            bloquear_controles(controles_actualizar, false);

            pnf_seleccionado.value = resultado.pnf.id

            actualizar_nombre_pnf.value = resultado.pnf.nombre;
            
            const option = document.createElement("option");
            option.value = resultado.pnf.periodo_academico;
            option.textContent = resultado.pnf.periodo_academico;
            option.selected = true;
            option.hidden = true;
            actualizar_periodo_academico.append(option);

            formulario_buscar.reset()
        } catch (error) {
            console.error(error);
        }
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
           const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/act_pnf/", {
                method: "POST",
                body: formulario,
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            formulario_actualizar.reset();
            bloquear_controles(controles_actualizar, true);
        } catch (error) {
            console.error(error);
        }
    });

});