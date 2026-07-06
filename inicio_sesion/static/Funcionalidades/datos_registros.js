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

    

    async function cargarPnfs(idNucleo, textoNucleo, contenedorPnf, nombrePnf, perfilId) {

        const csrftoken = getCookie("csrftoken");

        const idBloque = `pnf-${nombrePnf}-${idNucleo}`;

        // Si ya existe no volver a crearlo
        if (document.getElementById(idBloque))
            return;

        const response = await fetch("/pnfs_nucleos/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                id_nucleo: idNucleo,
                id_perfil: perfilId
            })
        });

        const data = await response.json();

        const bloque = document.createElement("div");
        bloque.className = "bloque-nucleo";
        bloque.id = idBloque;

        const titulo = document.createElement("h4");
        titulo.textContent = textoNucleo;

        bloque.appendChild(titulo);

        data.pnfs.forEach(pnf => {

            const label = document.createElement("label");
            label.style.display = "block";

            const check = document.createElement("input");

            check.type = "checkbox";
            check.name = nombrePnf;
            check.value = pnf.id_pnf;

            label.appendChild(check);
            label.append(" " + pnf.pnf);

            bloque.appendChild(label);

        });

        contenedorPnf.appendChild(bloque);

    }

    async function manejarContenedorPnf(evento, nombrePnf, contenedorPnfs, perfilId) {

        const checkbox = evento.target;

        const idNucleo = checkbox.value;

        const textoNucleo =
            checkbox.parentElement.textContent.trim();

        if (checkbox.checked) {

            contenedorPnfs.parentElement.style.display = "block";

            await cargarPnfs(
                idNucleo,
                textoNucleo,
                contenedorPnfs,
                nombrePnf,
                perfilId
            );

        } else {

            const bloque = document.getElementById(
                `pnf-${nombrePnf}-${idNucleo}`
            );

            if (bloque)
                bloque.remove();

            if (contenedorPnfs.children.length === 0)
                contenedorPnfs.parentElement.style.display = "none";
        }

    }

    document.addEventListener("change", async function(e){

        if(e.target.name==="nucleo_coordinador_pnf"){

            const perfil=document.querySelectorAll("input[name='perfil']:checked");

            const coordinador=[...perfil].find(x=>
                x.parentElement.textContent.trim()=="Coordinador de PNF"
            );

            if(!coordinador) return;

            manejarContenedorPnf(
                e,
                "pnf_coordinador_pnf",
                contenedorCheckboxPNFsCoordinador,
                coordinador.value
            );
        }

        if(e.target.name==="nucleo_docente"){

            const perfil=document.querySelectorAll("input[name='perfil']:checked");

            const docente=[...perfil].find(x=>
                x.parentElement.textContent.trim()=="Docente"
            );

            if(!docente) return;

            manejarContenedorPnf(
                e,
                "pnf_docente",
                contenedorCheckboxPNFsDocente,
                docente.value
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

        contenedor_gaceta.style.display = perfiles.includes("Director General") ? "block" : "none";

        contenedor_fecha_gaceta.style.display = perfiles.includes("Director General") ? "block" : "none";

        if (perfiles.includes("Encargado de Control de Estudio")) {

            contenedorNucleosControl.style.display = "block";

        } else {

            contenedorNucleosControl.style.display = "none";

            document.querySelectorAll(
                'input[name="nucleo_encargado_control_estudios"]'
            ).forEach(cb => cb.checked = false);
        }

        // Coordinador
        if (perfiles.includes("Coordinador de PNF")) {

            contenedorNucleosCoordinador.style.display = "block";

        } else {

            contenedorNucleosCoordinador.style.display = "none";
            contenedorPnfsCoordinador.style.display = "none";
            contenedorCheckboxPNFsCoordinador.innerHTML = "";

            document.querySelectorAll(
                'input[name="nucleo_coordinador_pnf"]'
            ).forEach(cb => cb.checked = false);
        }

        // Docente
        if (perfiles.includes("Docente")) {

            contenedorNucleosDocente.style.display = "block";

        } else {

            contenedorNucleosDocente.style.display = "none";
            contenedorPnfsDocente.style.display = "none";
            contenedorCheckboxPNFsDocente.innerHTML = "";

            document.querySelectorAll(
                'input[name="nucleo_docente"]'
            ).forEach(cb => cb.checked = false);
        }
    }
    cargarDatos();
});