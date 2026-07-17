document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registro_aulas")
    const formulario_actualizar = document.getElementById("formulario_actualizar_aula")
    const contenedor_aulas = document.getElementById("aulas_registradas")

    const select_nucleo_registrar = document.getElementById("registrar_nucleo_aula")

    const input_id_aula_oculto = document.getElementById("aula_seleccionar")
    const input_aula_actualizar = document.getElementById("actualizar_nombre_aula")
    const input_edificio_actualizar = document.getElementById("actualizar_nombre_edificio")
    const input_piso_actualizar = document.getElementById("actualizar_piso_edificio")
    const select_nucleo_actualizar = document.getElementById("actualizar_nucleo_aula")

    const dialogo_actualizar_aula = document.getElementById("dialogo_actualizar_aula")
    const mensajeError = document.getElementById("mensajede_error")
    const btn_cerrar_actualizar = document.getElementById("cerrar_dialogo")

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

    async function nucleos_registrados() {
        try {
            const respuesta = await fetch("/nucleos_registrados/")
            const resultado = await respuesta.json()

            select_nucleo_actualizar.innerHTML = "<option value=''>Seleccione el núcleo</option>"
            select_nucleo_registrar.innerHTML = "<option value=''>Seleccione el núcleo</option>"

            resultado.nucleos.forEach(nucleo => {
                const option_registrar = document.createElement("option")
                option_registrar.value = nucleo.id_nucleo
                option_registrar.textContent = nucleo.municipio
                select_nucleo_registrar.append(option_registrar)
                
                const option_actualizar = document.createElement("option")
                option_actualizar.value = nucleo.id_nucleo
                option_actualizar.textContent = nucleo.municipio
                select_nucleo_actualizar.append(option_actualizar)
            });

        } catch (error) {
            console.error(error);
        }
    }
    nucleos_registrados();

    async function aulas_registradas() {
        try {
            const respuesta = await fetch("/aulas_almacenadas/");
            const resultado = await respuesta.json();
            console.log(resultado);


            if (Object.keys(resultado).length === 0) {
                return;
            }
        
            Object.entries(resultado).forEach(([municipio, aulas]) => { 
                const tabla = document.createElement("table");
                tabla.classList.add("tabla_aulas");

                let filas = "";

                aulas.forEach((aula, index) => {
                    filas += `
                        <tr
                            data-id="${aula.id_aula}"
                            data-nombre="${aula.nombre_aula}"
                            data-edificio="${aula.nombre_edificio}"
                            data-piso="${aula.piso_edificio}"
                            data-nucleo="${aula.id_nucleo}">

                            <td>${index + 1}</td>
                            <td>${aula.nombre_aula}</td>
                            <td>${aula.nombre_edificio}</td>
                            <td>${aula.piso_edificio}</td>
                            <td>${aula.id_nucleo}</td>
                        </tr>
                    `;
                });

                tabla.innerHTML = `
                    <thead>
                        <tr>
                            <th colspan="5">${municipio}</th>
                        </tr>
                        <tr>
                            <th>#</th>
                            <th>Aula</th>
                            <th>Edificio</th>
                            <th>Piso</th>
                            <th>Municipio</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filas}
                    </tbody>
                `;

                contenedor_aulas.appendChild(tabla);
            });
            
        } catch (error) {
            console.error(error);
        }
    }
    aulas_registradas();

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)

            const respuesta = await fetch("/modulo_aula_academica/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json()
            console.log(resultado)

            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
            await aulas_registradas();
         
            formulario_registrar.reset()
        } catch (error) {
            console.error(error);
        }
    });

    contenedor_aulas.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr");
        console.log(fila.dataset.id)
        if (!fila) return;

        try {
            const formulario = new FormData()
            formulario.append("id_aula", fila.dataset.id)

            const respuesta = await fetch("/datos_aula/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado)
            dialogo_actualizar_aula.showModal()

            if (resultado.estado === "fallo") {
                mensajeError.textContent = resultado.descripcion;
                mensajeError.style.display = "block";

                setTimeout(() => {
                    mensajeError.textContent = "";
                    mensajeError.style.display = "none";
                }, 3000);

                return;
            }

            input_id_aula_oculto.value = resultado.id_aula
            input_aula_actualizar.value = resultado.nombre_aula
            input_edificio_actualizar.value = resultado.nombre_edificio
            input_piso_actualizar.value = resultado.piso_edificio
            
            const option_nucleo = document.createElement("option")
            option_nucleo.value = resultado.id_nucleo
            option_nucleo.textContent = resultado.municipio
            option_nucleo.selected = true
            option_nucleo.hidden = true
            select_nucleo_actualizar.append(option_nucleo)
        } catch (error) {
            console.error(error)
        }
    });

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar)

            const respuesta = await fetch("/actualizar_aula_academica/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json()
            console.log(resultado)

            dialogo_actualizar_aula.close()
            await aulas_registradas()
            
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

    btn_cerrar_actualizar.addEventListener("click", () => {
        dialogo_actualizar_aula.close()
    });
});