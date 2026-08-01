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

    function limpiarContenedores() {
        ocultar_elementos();

        // Limpiar los PNFs generados dinámicamente
        contenedorCheckboxPNFsCoordinador.innerHTML = "";
        contenedorCheckboxPNFsDocente.innerHTML = "";

        // Desmarcar todos los checkbox
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
    }

    document.addEventListener("submit", function () {
        limpiarContenedores();
    });

    function ocultar_elementos() {

        contenedorNucleosControl.style.display = "none";
        contenedorNucleosCoordinador.style.display = "none";
        contenedorNucleosDocente.style.display = "none";

        contenedorPnfsCoordinador.style.display = "none";
        contenedorPnfsDocente.style.display = "none";
    }
    ocultar_elementos();

    // Crear los controles checkbox de los núcleos para todos los perfiles
    function cargarNucleos(contenedor, nucleos, nombreCampo) {
        contenedor.innerHTML = "";

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

    // Obtener los perfiles para crear los checkbox
    async function cargarDatos() {
        try {
            const respuesta = await fetch("/datos_perfiles/");
            const resultado = await respuesta.json();

            contenedorCheckboxPerfiles.innerHTML = "";

            resultado.perfiles.forEach(perfil => {
                const label = document.createElement("label");
                label.style.display = "block";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "perfil";
                checkbox.value = perfil.id_perfil;
                checkbox.dataset.perfil = perfil.perfil;

                label.appendChild(checkbox);
                label.append(" " + perfil.perfil);

                contenedorCheckboxPerfiles.appendChild(label);
            });

            cargarNucleos(
                contenedorCheckboxNucleosEncargado,
                resultado.nucleos,
                "nucleo_encargado_control_estudios"
            );

            cargarNucleos(
                contenedorCheckboxNucleosCoordinador,
                resultado.nucleos,
                "nucleo_coordinador_pnf"
            );

            cargarNucleos(
                contenedorCheckboxNucleosDocente,
                resultado.nucleos,
                "nucleo_docente"
            );

        } catch (error) {
            console.error(error);
        }
    }
    cargarDatos();

    // Obtener todos los pnfs y crear todos los checkbox
    async function cargarPnfs(idNucleo, textoNucleo, contenedorPnf, nombrePnf, perfil) {

        const idBloque = `pnf-${nombrePnf}-${idNucleo}`;

        if (document.getElementById(idBloque))
            return;

        const respuesta = await fetch("/pnfs_disp/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                id_nucleo: idNucleo,
                perfil: perfil
            })
        });

        const resultado = await respuesta.json();
        console.log(resultado);

        const bloque = document.createElement("div");
        bloque.className = "bloque-nucleo";
        bloque.id = idBloque;

        const titulo = document.createElement("h4");
        titulo.textContent = textoNucleo;

        bloque.appendChild(titulo);

        resultado.pnfs.forEach(pnf => {

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

    async function manejarContenedorPnf(evento, nombrePnf, contenedorPnfs, perfil) {

        const checkbox = evento.target;

        const idNucleo = checkbox.value;
        const textoNucleo = checkbox.parentElement.textContent.trim();

        if (checkbox.checked) {

            contenedorPnfs.parentElement.style.display = "block";

            await cargarPnfs(
                idNucleo,
                textoNucleo,
                contenedorPnfs,
                nombrePnf,
                perfil
            );

        } else {

            const bloque = document.getElementById(`pnf-${nombrePnf}-${idNucleo}`);

            if (bloque)
                bloque.remove();

            if (contenedorPnfs.children.length === 0)
                contenedorPnfs.parentElement.style.display = "none";
        }
    }
    // 
    document.addEventListener("change", async function (e) {

        if (e.target.name === "nucleo_coordinador_pnf") {

            const coordinador = [...document.querySelectorAll("input[name='perfil']:checked")]
                .find(cb => cb.dataset.perfil === "Coordinador PNF");

            if (!coordinador)
                return;

            await manejarContenedorPnf(
                e,
                "pnf_coordinador_pnf",
                contenedorCheckboxPNFsCoordinador,
                coordinador.dataset.perfil
            );
        }

        if (e.target.name === "nucleo_docente") {

            const docente = [...document.querySelectorAll("input[name='perfil']:checked")]
                .find(cb => cb.dataset.perfil === "Docente");

            if (!docente)
                return;

            await manejarContenedorPnf(
                e,
                "pnf_docente",
                contenedorCheckboxPNFsDocente,
                docente.dataset.perfil
            );
        }

    });

    async function cargarNucleosPorPerfil(perfil, contenedor, nombreCampo) {

        const respuesta = await fetch("/nucleos_disp/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                perfil: perfil
            })
        });

        const resultado = await respuesta.json();

        cargarNucleos(
            contenedor,
            resultado.nucleos,
            nombreCampo
        );
    }

    document.addEventListener("change", async function (e) {

        if (e.target.name !== "perfil")
            return;

        const perfil = e.target.dataset.perfil;

        if (perfil === "Control de Estudio") {

            await cargarNucleosPorPerfil(
                perfil,
                contenedorCheckboxNucleosEncargado,
                "nucleo_encargado_control_estudios"
            );

        }

        validarPerfiles();
    });

    function validarPerfiles() {

    const perfiles = [...document.querySelectorAll("input[name='perfil']:checked")]
        .map(cb => cb.dataset.perfil);

        contenedorNucleosControl.style.display =
            perfiles.includes("Control de Estudio") ? "block" : "none";

        contenedorNucleosCoordinador.style.display =
            perfiles.includes("Coordinador PNF") ? "block" : "none";

        contenedorNucleosDocente.style.display =
            perfiles.includes("Docente") ? "block" : "none";

        if (!perfiles.includes("Control de Estudio")) {
            document.querySelectorAll(
                'input[name="nucleo_encargado_control_estudios"]'
            ).forEach(cb => cb.checked = false);
        }

        if (!perfiles.includes("Coordinador PNF")) {

            contenedorPnfsCoordinador.style.display = "none";
            contenedorCheckboxPNFsCoordinador.innerHTML = "";

            document.querySelectorAll(
                'input[name="nucleo_coordinador_pnf"]'
            ).forEach(cb => cb.checked = false);
        }

        if (!perfiles.includes("Docente")) {

            contenedorPnfsDocente.style.display = "none";
            contenedorCheckboxPNFsDocente.innerHTML = "";

            document.querySelectorAll(
                'input[name="nucleo_docente"]'
            ).forEach(cb => cb.checked = false);
        }
    }
    
});