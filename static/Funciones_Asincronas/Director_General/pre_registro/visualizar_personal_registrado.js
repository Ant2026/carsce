document.addEventListener("DOMContentLoaded", () => {

    const contenedor_personal_registrado = document.getElementById("contenedor_personal_registrado");

    const select_nacionalidad = document.getElementById("nacionalidad");
    const input_cedula = document.getElementById("cedula");

    const select_pnf_registrados = document.getElementById("pnf_registrados");
    const perfiles_registrados = document.getElementById("perfiles_registrados");

    let pnf, perfil;

    async function pnfs_registrados() {
        try {
            const respuesta = await fetch("/pnfs_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_pnf_registrados.innerHTML = "<option value='' selected>Selecciona un P.N.F</option>";

            resultado.nucleos.forEach(nucleo => {
                nucleo.pnfs.forEach(pnf => {
                    const option = document.createElement("option");
                    option.value = pnf.id_pnf;
                    option.textContent = pnf.pnf;
                    select_pnf_registrados.appendChild(option);
                });
            });
        } catch (error) {
            console.error(error);
        }
    }
    pnfs_registrados();

    select_pnf_registrados.addEventListener("change", async () => {
        pnf = select_pnf_registrados.value;
        await personal_registrados();
    });

    perfiles_registrados.addEventListener("change", async () => {
        perfil = perfiles_registrados.value;
        await personal_registrados();
    });

    async function personal_registrados() {
        try {
            const formulario = new FormData();
            formulario.append("pnf", pnf || "");
            formulario.append("perfil", perfil || "");

            const respuesta = await fetch("/per_reg_asig/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            console.log("PNF:", pnf);
            console.log("Perfil:", perfil);
            console.log("Resultado:", resultado);

            // Limpiar tabla
            contenedor_personal_registrado.innerHTML = "";

            // Crear nuevamente las filas
            resultado.personal.forEach((persona, index) => {

                const fila = document.createElement("tr");

                fila.innerHTML = `
                <td>${index + 1}</td>
                <td>${persona.nombres}</td>
                <td>${persona.apellidos}</td>
                <td>${persona.cedula}</td>
                <td>${persona.rol}</td>
                <td>${persona.pnf}</td>
            `;

                contenedor_personal_registrado.appendChild(fila);
            });

        } catch (error) {
            console.error(error);
        }
    }
    personal_registrados();

});