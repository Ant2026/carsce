document.addEventListener("DOMContentLoaded", () => {

    const contenedor = document.getElementById("tabla_pnfs");
    const btn_cerrar = document.getElementById("cerrar_dialogo");
    const dialog = document.getElementById("dialogo_actualizar_pnfs");

    const contenedor_nucleos = document.getElementById("contenedor_actualizar_nucleos");
    const formulario_actualizar_pnf = document.getElementById("modificarpnf")
    const input_actualizar_pnf = document.getElementById("actualizar_nombre_pnf");
    const input_actualizar_codigo_pnf = document.getElementById("actualizar_codigo_pnf");
    const select_actualizar_periodo_academico = document.getElementById("actualizar_periodo_academico")
    const input_oculto_pnf = document.getElementById("pnf_seleccionado");
    
    const formulario_registrar_pnf = document.getElementById("registrarpnf");
    const input_registrar_pnf = document.getElementById("registrar_nombre_pnf");
    const input_registrar_codigo = document.getElementById("registrar_codigo_pnf");
    const select_registrar_periodo_academico = document.getElementById("registrar_periodo_academico")
    const contenedor_registrar_nucleos = document.getElementById("contenedor_registrar_nucleos");

    let pnf = "", nucleo = ""

    input_registrar_codigo.addEventListener("input", function () {
        this.value = this.value.replace(/[^A-Za-z0-9]/g, "");
    });

    async function cargar() {
        try {
            const respuesta = await fetch("/pnfs_registrada/");
            const resultado = await respuesta.json();

            contenedor.innerHTML = "";

            const nucleosMap = {};
            resultado.pnfs.forEach(pnf => {
                pnf.nucleos.forEach(nucleo => {

                    if (!nucleosMap[nucleo.id_nucleo]) {
                        nucleosMap[nucleo.id_nucleo] = {
                            id: nucleo.id_nucleo,
                            municipio: nucleo.municipio,
                            pnfs: []
                        };
                    }

                    nucleosMap[nucleo.id_nucleo].pnfs.push({
                        id_pnf: pnf.id_pnf,
                        pnf: pnf.pnf,
                        codigo: pnf.codigo
                    });
                });
            });

            Object.values(nucleosMap).forEach(nucleo => {

                const table = document.createElement("table");
                table.classList.add("tabla_nucleo");

                let filas = "";

                nucleo.pnfs.forEach((pnf, index) => {
                    filas += `
                        <tr
                            data-id-nucleo="${nucleo.id}"
                            data-municipio="${nucleo.municipio}"
                            data-id-pnf="${pnf.id_pnf}"
                            data-pnf="${pnf.pnf}">
                            <td>${index + 1}</td>
                            <td>${pnf.pnf}</td>
                        </tr>
                    `;
                });

                table.innerHTML = `
                    <thead>
                        <tr>
                            <th colspan="2">
                                Núcleo: ${nucleo.municipio}
                            </th>
                        </tr>
                        <tr>
                            <th>ID PNF</th>
                            <th>PNF</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filas}
                    </tbody>
                `;
                contenedor.appendChild(table);
            });

        } catch (error) {
            console.error(error);
        }
    }
    cargar();

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

    contenedor.addEventListener("click", async function (e) {
        const fila = e.target.closest("tr");
        if (!fila || !fila.dataset.idPnf) return;

        try {
            pnf = fila.dataset.idPnf
            nucleo = fila.dataset.idnucleo

            const formulario = new FormData();
            formulario.append("pnf", pnf);
            const respuesta = await fetch("/datos_pnf/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            input_oculto_pnf.value = pnf
            input_actualizar_pnf.value = resultado.pnf.nombre;
            input_actualizar_codigo_pnf.value = resultado.pnf.codigo;
            
            const option = document.createElement("option")
            option.value = resultado.pnf.periodo_academico
            option.textContent = resultado.pnf.periodo_academico
            option.selected = true
            option.hidden = true
            select_actualizar_periodo_academico.append(option) 
            
            contenedor_nucleos.innerHTML = "";

            const idsAsignados = resultado.nucleos.map(nucleo => Number(nucleo.id));
            resultado.todos_nucleos.forEach(nucleo => {
                const contenedorCheck = document.createElement("div");
                const checkbox = document.createElement("input");

                checkbox.type = "checkbox";
                checkbox.name = "nucleo";
                checkbox.value = nucleo.id;

                if (idsAsignados.includes(Number(nucleo.id))) {
                    checkbox.checked = true;
                }

                const label = document.createElement("label");

                label.textContent = nucleo.municipio;

                contenedorCheck.appendChild(checkbox);
                contenedorCheck.appendChild(label);

                contenedor_nucleos.appendChild(contenedorCheck);
            });

            dialog.showModal();
        } catch (error) {
            console.error(error);
        }
    });

    btn_cerrar.addEventListener("click", () => {
        document.getElementById("dialogo_actualizar_pnfs").close();
    });

    formulario_actualizar_pnf.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar_pnf)
            const respuesta = await fetch("/guardar_actuailizacion_pnf/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()
   
            dialog.close();
            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            await cargar()
        } catch (error) {
            console.error(error)
        }        
    });

    async function nucleos_seleccionar() {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();

            contenedor_registrar_nucleos.innerHTML = ""

            resultado.nucleos.forEach(nucleo => {
                const checkbox = document.createElement("input");

                checkbox.type = "checkbox";
                checkbox.name = "nucleos";
                checkbox.value = nucleo.id_nucleo;

                const label =
                    document.createElement("label");

                label.textContent = nucleo.municipio;

                label.appendChild(checkbox);

                contenedor_registrar_nucleos.appendChild(label);
            });
        } catch (error) {
            console.error(error)
        }
    }
    nucleos_seleccionar()

    formulario_registrar_pnf.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar_pnf)

            const respuesta = await fetch("/modulo_pnf/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()

            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            await cargar()

            formulario_registrar_pnf.reset()
        } catch (error) {
            console.error(error)
        }
    })
});