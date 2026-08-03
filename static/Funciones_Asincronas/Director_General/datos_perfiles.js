document.addEventListener("DOMContentLoaded", function () {
    
    const contenedorPnfsCoordinador = document.getElementById("contenedor_pnfs_coordinador_pnf");
    const contenedorPnfsDocente = document.getElementById("contenedor_pnfs_docente");
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
        contenedorPnfsCoordinador.style.display = "none";
        contenedorPnfsDocente.style.display = "none";
    }
    ocultar_elementos();

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
        } catch (error) {
            console.error(error);
        }
    }
    cargarDatos();

    // Obtener todos los pnfs y crear todos los checkbox
    async function cargarPnfs(contenedorPnf, nombrePnf, idPerfil) {

        contenedorPnf.innerHTML = "";

        const respuesta = await fetch("/pnfs_disp/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                id_perfil: idPerfil
            })
        });

        const resultado = await respuesta.json();

        resultado.pnfs.forEach(pnf => {

            const label = document.createElement("label");
            label.style.display = "block";

            const check = document.createElement("input");
            check.type = "checkbox";
            check.name = nombrePnf;
            check.value = pnf.id_pnf;

            label.appendChild(check);
            label.append(" " + pnf.pnf);

            contenedorPnf.appendChild(label);
        });
    }

    document.addEventListener("change", async function (e) {

        if (e.target.name !== "perfil")
            return;

        const perfil = e.target.dataset.perfil;
        const idPerfil = parseInt(e.target.value);

        if (perfil === "Coordinador PNF") {

            contenedorPnfsCoordinador.style.display =
                e.target.checked ? "block" : "none";

            if (e.target.checked) {
                await cargarPnfs(
                    contenedorCheckboxPNFsCoordinador,
                    "pnf_coordinador_pnf",
                    idPerfil
                );
            } else {
                contenedorCheckboxPNFsCoordinador.innerHTML = "";
            }
        }

        if (perfil === "Docente") {

            contenedorPnfsDocente.style.display =
                e.target.checked ? "block" : "none";

            if (e.target.checked) {
                await cargarPnfs(
                    contenedorCheckboxPNFsDocente,
                    "pnf_docente",
                    idPerfil
                );
            } else {
                contenedorCheckboxPNFsDocente.innerHTML = "";
            }
        }
});
});