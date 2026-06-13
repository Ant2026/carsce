document.addEventListener("DOMContentLoaded", function () {
    const contenedorNucleosControl = document.getElementById("contenedor_nucleos_encargado_control_estudios");
    const contenedorNucleosCoordinador = document.getElementById("contenedor_nucleos_coordinador_pnf");
    const contenedorNucleosDocente = document.getElementById("contenedor_nucleos_docente");
    const contenedorPnfsCoordinador = document.getElementById("contenedor_pnfs_coordinador_pnf");
    const contenedorPnfsDocente = document.getElementById("contenedor_pnfs_docente");

    const contenedorCheckboxNucleosEncargado = document.getElementById("nucleo_encargado_control_estudios");
    const contenedorCheckboxNucleosCoordinador = document.getElementById("nucleo_coordinador_pnf");
    const contenedorCheckboxNucleosDocente = document.getElementById("nucleo_docente");

    const contenedorCheckboxPerfiles = document.getElementById("perfil");

    const contenedorCheckboxPNFsCoordinador = document.getElementById("pnf_coordinador_pnf");
    const contenedorCheckboxPNFsDocente = document.getElementById("pnf_docente");

    const contenedor_gaceta = document.getElementById("contenedor_gaceta");
    const contenedor_fecha_gaceta = document.getElementById("contenedor_fecha_gaceta");

    function ocultar_elementos() {

        contenedor_gaceta.style.display = "none";
        contenedor_fecha_gaceta.style.display = "none";

        contenedorNucleosControl.style.display = "none";
        contenedorNucleosCoordinador.style.display = "none";
        contenedorNucleosDocente.style.display = "none";

        contenedorPnfsCoordinador.style.display = "none";
        contenedorPnfsDocente.style.display = "none";
    }
    ocultar_elementos();

    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function cargarNucleos(contenedor, nucleos, nombreCampo) {
        contenedor.innerHTML = "";
        console.log("Cargando:", contenedor);
        nucleos.forEach(nucleo => {

            const label = document.createElement("label");
            label.style.display = "block";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.name = nombreCampo;
            checkbox.value = nucleo.id_nucleo;

            label.appendChild(checkbox);
            label.append(" " + nucleo.municipio);

            contenedor.appendChild(label);
        });
    }

    async function cargarDatos() {
        try {
            const response = await fetch("/datos_registro/");
            const data = await response.json();
            console.log(data);
            
            contenedorCheckboxPerfiles.innerHTML = "";
            
            data.perfiles.forEach(perfil => {

                const label = document.createElement("label");
                label.style.display = "block";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "perfil";
                checkbox.value = perfil.id_pefil;

                label.appendChild(checkbox);
                label.append(" " + perfil.perfil);

                contenedorCheckboxPerfiles.appendChild(label);
            });

            // Núcleos
            cargarNucleos(
                contenedorCheckboxNucleosEncargado,
                data.nucleos, 
                "nucleo_encargado_control_estudios"
            );

            cargarNucleos(
                contenedorCheckboxNucleosCoordinador,
                data.nucleos, 
                "nucleo_coordinador_pnf"    
            );

            cargarNucleos(
                contenedorCheckboxNucleosDocente,
                data.nucleos,
                "nucleo_docente"
            );

        } catch (error) {
            console.error("Error cargando datos:", error);
        }
    }

    function getPerfilesSeleccionados() {
        return Array.from(
            document.querySelectorAll('input[name="perfil"]:checked')
        ).map(cb => cb.value);
    }

    

    async function cargarPnfs(nombreNucleo, contenedorPnf, nombrePnf) {

        const nucleos = document.querySelectorAll(
            `input[name="${nombreNucleo}"]:checked`
        );

        contenedorPnf.innerHTML = "";

        const csrftoken = getCookie("csrftoken");

        for (const nucleo of nucleos) {

            const response = await fetch("/pnfs_nucleos/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify({
                    id_nucleo: nucleo.value
                }),
            });

            const data = await response.json();

            // Contenedor del núcleo
            const bloqueNucleo = document.createElement("div");
            bloqueNucleo.classList.add("bloque-nucleo");

            const titulo = document.createElement("h4");
            titulo.textContent = nucleo.parentElement.textContent.trim();

            bloqueNucleo.appendChild(titulo);

            data.pnfs.forEach(pnf => {

                const label = document.createElement("label");
                label.style.display = "block";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = nombrePnf;
                checkbox.value = pnf.id_pnf;

                label.appendChild(checkbox);
                label.append(" " + pnf.pnf);

                bloqueNucleo.appendChild(label);
            });

            contenedorPnf.appendChild(bloqueNucleo);
        }
    }

    function manejarContenedorPnf(nombreNucleo, contenedor, contenedorCheckbox, nombrePnf) {

        const seleccionados = document.querySelectorAll(
            `input[name="${nombreNucleo}"]:checked`
        );

        if (seleccionados.length === 0) {
            contenedor.style.display = "none";
            contenedorCheckbox.innerHTML = "";
            return;
        }

        contenedor.style.display = "block";

        cargarPnfs(
            nombreNucleo,
            contenedorCheckbox,
            nombrePnf
        );
    }

    document.addEventListener("change", function (e) {
        if (e.target.name === "perfil") {
            validarPerfiles();
        }

        if (e.target.name === "nucleo_coordinador_pnf") {
            manejarContenedorPnf(
                "nucleo_coordinador_pnf",
                contenedorPnfsCoordinador,
                contenedorCheckboxPNFsCoordinador,
                "pnf_coordinador_pnf"
            );
        }

        if (e.target.name === "nucleo_docente") {
            manejarContenedorPnf(
                "nucleo_docente",
                contenedorPnfsDocente,
                contenedorCheckboxPNFsDocente,
                "pnf_docente"
            );
        }
    });

    async function cargarNucleosPorPerfil(perfilId,contenedor,nombreCampo) {
        const csrftoken = getCookie("csrftoken");

        const response = await fetch("/validar_nucleos/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                id_perfil: perfilId
            }),
        });

        const data = await response.json();

        cargarNucleos(
            contenedor,
            data.nucleos,
            nombreCampo
        );
    }

    document.addEventListener("change", async function (e) {
        if (e.target.name === "perfil") {
            const perfilId = e.target.value;
            const nombrePerfil = e.target.parentElement.textContent.trim();

            if (nombrePerfil === "Encargado de Control de Estudio") {
                await cargarNucleosPorPerfil(
                    perfilId,
                    contenedorCheckboxNucleosEncargado,
                    "nucleo_encargado_control_estudios"
                );
            }

            validarPerfiles();
        }
    });

    function validarPerfiles() {
        const perfiles = Array.from(
            document.querySelectorAll('input[name="perfil"]:checked')
        ).map(cb => cb.parentElement.textContent.trim());

        ocultar_elementos();

        if (perfiles.includes("Director General")) {
            contenedor_gaceta.style.display = "block";
            contenedor_fecha_gaceta.style.display = "block";
        }
        if (perfiles.includes("Encargado de Control de Estudio")) {
            contenedorNucleosControl.style.display = "block";
        }
        if (perfiles.includes("Coordinador de PNF")) {
            contenedorNucleosCoordinador.style.display = "block";
            contenedorPnfsCoordinador.style.display = "none";
        }
        if (perfiles.includes("Docente")) {
            contenedorNucleosDocente.style.display = "block";
            contenedorPnfsDocente.style.display = "none";
        }
    }

    cargarDatos();
});