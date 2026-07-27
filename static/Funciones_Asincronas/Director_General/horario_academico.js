document.addEventListener("DOMContentLoaded", () => {

    const inputCantidadFila = document.getElementById("cantidad_fila");
    const contenedorHorario = document.getElementById("contenedor_horario");
    const btn_generar_pnf = document.getElementById("generar_pdf")
    
    const select_pnfs_registrado = document.getElementById("pnfs_registrados")

    let pnf = ""

    async function pnfs_registrado() {
        try {
            const respuesta = await fetch("/pnfs_registrada/");
            const resultado = await respuesta.json();
            console.log(resultado)

            select_pnfs_registrado.innerHTML = "<option selected>Seleccione el PNF</option>"

            resultado.pnfs.forEach(pnf => {
                const option = document.createElement("option")
                option.value = pnf.id_pnf
                option.textContent = pnf.pnf

                select_pnfs_registrado.append(option)
            });
        } catch (error) {
            console.error(error)
        }
    }
    pnfs_registrado();
    
    select_pnfs_registrado.addEventListener("change", () => {
        pnf = select_pnfs_registrado.value
    });



    inputCantidadFila.addEventListener("keydown", (e) => {

        // Permitir teclas de control
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

        // Solo permitir números del 1 al 8
        if (!/^[1-8]$/.test(e.key)) {
            e.preventDefault();
        }

    });
  
    inputCantidadFila.addEventListener("input", () => {

        // Eliminar cualquier carácter que no sea un número
        inputCantidadFila.value = inputCantidadFila.value.replace(/\D/g, "");

        let cantidad = parseInt(inputCantidadFila.value);


        if (inputCantidadFila.value.length > 1) {
            inputCantidadFila.value = inputCantidadFila.value.charAt(0);
        }

        // Si está vacío
        if (isNaN(cantidad)) {
            contenedorHorario.innerHTML = "";
            return;
        }

        // Limitar entre 1 y 8
        if (cantidad < 1) {
            cantidad = 1;
            inputCantidadFila.value = 1;
        }

        if (cantidad > 8) {
            cantidad = 8;
            inputCantidadFila.value = 8;
        }

        // Limpiar la tabla
        contenedorHorario.innerHTML = "";

        // Crear filas
        for (let i = 0; i < cantidad; i++) {

            const fila = document.createElement("tr");

            // Hora Inicio
            const tdInicio = document.createElement("td");

            const inputInicio = document.createElement("input");
            inputInicio.type = "time";
            inputInicio.required = true;

            tdInicio.appendChild(inputInicio);
            fila.appendChild(tdInicio);

            // Hora Final
            const tdFinal = document.createElement("td");

            const inputFinal = document.createElement("input");
            inputFinal.type = "time";
            inputFinal.required = true;

            tdFinal.appendChild(inputFinal);
            fila.appendChild(tdFinal);

            // Lunes a Viernes
            for (let j = 0; j < 5; j++) {

                const td = document.createElement("td");

                const inputMateria = document.createElement("input");
                inputMateria.type = "text";
                inputMateria.placeholder = "Materia";

                td.appendChild(inputMateria);
                fila.appendChild(td);
            }

            contenedorHorario.appendChild(fila);
        }

    });

    btn_generar_pnf.addEventListener("click", async (e) => {

        e.preventDefault();

        const horario = [];

        document.querySelectorAll("#contenedor_horario tr").forEach(fila => {

            const inputs = fila.querySelectorAll("input");

            horario.push({
                hora_inicio: inputs[0].value,
                hora_final: inputs[1].value,
                lunes: inputs[2].value,
                martes: inputs[3].value,
                miercoles: inputs[4].value,
                jueves: inputs[5].value,
                viernes: inputs[6].value
            });

        });

        try{

            const respuesta = await fetch("/modulo_horario_academico/",{

                method:"POST",

                headers:{
                    "Content-Type":"application/json",
                    "X-CSRFToken":document.querySelector("[name=csrfmiddlewaretoken]").value
                },

                body:JSON.stringify({
                    horario:horario
                })

            });

            const blob = await respuesta.blob();

            const url = window.URL.createObjectURL(blob);

            const enlace = document.createElement("a");
            enlace.href = url;
            enlace.download = "Horario_Academico.pdf";
            enlace.click();

            window.URL.revokeObjectURL(url);

        }catch(error){
            console.error(error);
        }

    });
});