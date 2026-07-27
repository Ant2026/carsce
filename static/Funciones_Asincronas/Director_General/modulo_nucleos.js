document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("registrarnucleo")
    const select_registrar_municipio = document.getElementById("registrar_municipio")
    const textarea_registrar_direccion = document.getElementById("registrar_direccion")

    const contenedor_nucleos = document.getElementById("tabla_nucleo")

    const dialogo_actualizar = document.getElementById("dialogo_actualizar_nucleos")
    const btn_cerrar = document.getElementById("cerrar_dialogo")
    const formulario_actualizar = document.getElementById("modificarnucleo")
    const input_nucleo_oculto = document.getElementById("nucleo_seleccionado")
    const select_actualizar_municipio = document.getElementById("actualizar_municipio")
    const textarea_actualizar_direccion = document.getElementById("actualizar_direccion_nucleo")
    
    let municipios_Barinas = [
        "Alberto Arvelo Torrealba",
        "Andrés Eloy Blanco",
        "Antonio José de Sucre",
        "Arismendi",
        "Barinas",
        "Bolívar",
        "Cruz Paredes",
        "Ezequiel Zamora",
        "Obispos",
        "Pedraza",
        "Rojas",
        "Sosa"
    ];

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
   
    async function municipiosBarinasRegistrar() {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();

            select_registrar_municipio.innerHTML = '<option value="" selected>Elije el municipio</option>';

            const registrados = (resultado.nucleos || []).map(n => n.municipio);

            municipios_Barinas
                .filter(municipio => !registrados.includes(municipio))
                .forEach(municipio => {
                    console.log("Agregando:", municipio);

                    const option = document.createElement("option");
                    option.value = municipio;
                    option.textContent = municipio;
                    select_registrar_municipio.appendChild(option);
                });

        } catch (error) {
            console.error(error);
        }
    }

    municipiosBarinasRegistrar();

    async function cargar() {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();

            contenedor_nucleos.innerHTML = "";

            let filas = "";

            resultado.nucleos.forEach((nucleo, index) => {
                filas += `
                    <tr
                        data-id-nucleo="${nucleo.id_nucleo}"
                        data-municipio="${nucleo.municipio}"
                    >
                        <td>${index + 1}</td>
                        <td>${nucleo.municipio}</td>
                        <td>${nucleo.direccion}</td>
                    </tr>
                `;
            });

            contenedor_nucleos.innerHTML = `
                <table class="tabla_nucleo">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Municipio</th>
                            <th>Dirección</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filas}
                    </tbody>
                </table>
            `;

        } catch (error) {
            console.error(error);
        }
    }
    cargar();

    async function municipiosBarinasActualizar() {
        try {
            const respuesta = await fetch("/nucleos_registrados/");
            const resultado = await respuesta.json();

            const registrados = resultado.nucleos.map(nucleo => nucleo.municipio);

            municipios_Barinas.filter(municipio => 
                !registrados.includes(municipio)).forEach(municipio => {
                const option = document.createElement("option");
                option.value = municipio;
                option.textContent = municipio;
                select_actualizar_municipio.appendChild(option);
            });

        } catch (error) {
            console.error(error);
        }
    }
    municipiosBarinasActualizar();

    contenedor_nucleos.addEventListener("click", async function (e) {
        const fila = e.target.closest("tr");
        if (!fila || !fila.dataset.idNucleo) return;

        try {
            const formulario = new FormData();
            formulario.append("nucleo", fila.dataset.idNucleo);

            const respuesta = await fetch("/datos_nucleo/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            input_nucleo_oculto.value = resultado.nucleo.id;

            select_actualizar_municipio.innerHTML = "";

            const option_registrado = document.createElement("option")
            option_registrado.textContent = resultado.nucleo.municipio
            option_registrado.value = resultado.nucleo.municipio
            option_registrado.selected = true
            select_actualizar_municipio.appendChild(option_registrado)

            municipiosBarinasActualizar()

            textarea_actualizar_direccion.value = resultado.nucleo.direccion;

            dialogo_actualizar.showModal();
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
            const formulario = new FormData(formulario_actualizar)

            const respuesta = await fetch("/guardar_actualizacion_nucleo/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()

            dialogo_actualizar.close();
            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_actualizar.reset()
        } catch (error) {
            console.error(error)
        }
    });

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)

            const respuesta = await fetch("/modulo_nucleo/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json()

            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_registrar.reset()
        } catch (error) {
            console.error(error)
        }
    });
});