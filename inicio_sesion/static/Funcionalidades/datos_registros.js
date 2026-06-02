document.addEventListener("DOMContentLoaded", function () {

    const contenedorPerfiles = document.getElementById("perfil");
    const contenedorNucleos = document.getElementById("nucleo");
    const contenedorPnfs = document.getElementById("pnf");

    const contenedor_gaceta = document.getElementById("contenedor_gaceta");
    const contenedor_fecha_gaceta = document.getElementById("contenedor_fecha_gaceta");

    contenedor_nucleos.style.display = "none";
    contenedor_pnfs.style.display = "none";

    contenedor_gaceta.style.display = "none";
    contenedor_fecha_gaceta.style.display = "none";

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

    async function cargarDatos() {
        try {
            const response = await fetch("/datos_registro/");
            const data = await response.json();

            contenedorPerfiles.innerHTML = "";
            data.perfiles.forEach(perfil => {
                const label = document.createElement("label");
                label.style.display = "block";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "perfil";
                checkbox.value = perfil.id_pefil;

                label.appendChild(checkbox);
                label.append(" " + perfil.perfil);

                contenedorPerfiles.appendChild(label);
            });

            contenedorNucleos.innerHTML = "";
            data.nucleos.forEach(nucleo => {
                const label = document.createElement("label");
                label.style.display = "block";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "nucleo";
                checkbox.value = nucleo.id_nucleo;

                label.appendChild(checkbox);
                label.append(" " + nucleo.municipio);

                contenedorNucleos.appendChild(label);
            });
        } catch (error) {
            console.error("Error cargando datos iniciales:", error);
        }
    }

    function getPerfilesSeleccionados() {
        return Array.from(
            document.querySelectorAll('input[name="perfil"]:checked')
        ).map(cb => cb.value);
    }

    async function cargarPnfs() {
        const nucleos = document.querySelectorAll('input[name="nucleo"]:checked');
        const idNucleo = Array.from(nucleos)[0]?.value;

        if (!idNucleo) return;

        const csrftoken = getCookie('csrftoken');

        const response = await fetch('/pnfs_nucleos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ id_nucleo: idNucleo }),
        });

        const data = await response.json();

        contenedorPnfs.innerHTML = "";

        data.pnfs.forEach(pnf => {

            const label = document.createElement("label");
            label.style.display = "block";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.name = "pnf";
            checkbox.value = pnf.id_pnf;

            label.appendChild(checkbox);
            label.append(" " + pnf.pnf);

            contenedorPnfs.appendChild(label);
        });
    }

    function validarPerfiles() {
        const perfilesSeleccionados = document.querySelectorAll('input[name="perfil"]:checked');

        if (perfilesSeleccionados.length === 0) {

            contenedor_nucleos.style.display = "none";
            contenedor_pnfs.style.display = "none";

            contenedor_gaceta.style.display = "none";
            contenedor_fecha_gaceta.style.display = "none";

            return;
        }

        const perfiles = Array.from(perfilesSeleccionados)
            .map(cb => cb.parentElement.textContent.trim());

        const esDirector = perfiles.includes("Director General");
        const esControlEstudio = perfiles.includes("Encargado de Control de Estudio");

        if (esDirector) {

            contenedor_nucleos.style.display = "none";
            contenedor_pnfs.style.display = "none";

            contenedor_gaceta.style.display = "block";
            contenedor_fecha_gaceta.style.display = "block";

            document.querySelectorAll('input[name="nucleo"]').forEach(c => c.checked = false);
            document.querySelectorAll('input[name="pnf"]').forEach(c => c.checked = false);

        } else if (esControlEstudio) {

            contenedor_nucleos.style.display = "block";
            contenedor_pnfs.style.display = "none";

            contenedor_gaceta.style.display = "none";
            contenedor_fecha_gaceta.style.display = "none";

            document.querySelectorAll('input[name="pnf"]').forEach(c => c.checked = false);

        } else {

            contenedor_nucleos.style.display = "block";
            contenedor_pnfs.style.display = "block";

            contenedor_gaceta.style.display = "none";
            contenedor_fecha_gaceta.style.display = "none";
        }
    }

    document.addEventListener("change", function (e) {

        if (e.target.name === "perfil") {
            validarPerfiles();
        }

        if (e.target.name === "nucleo") {
            cargarPnfs(); // si aplica
        }
    });

    document.addEventListener("change", function (e) {
        if (e.target.name === "perfil") {

            // solo 1 checkbox permitido
            document.querySelectorAll('input[name="perfil"]').forEach(cb => {
                if (cb !== e.target) cb.checked = false;
            });

            validarPerfiles();
        }
    });


    cargarDatos();
});