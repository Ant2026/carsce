document.addEventListener("DOMContentLoaded", () => {
    
    const select_busqueda_pnf = document.getElementById("buscar_pnf");
    const contenedor_materias = document.getElementById("contenedor_tablas_materia");
    
    let pnf = "";

    async function pnfs_registrados() {
        try {
            const respuesta = await fetch("/pnfs_reg/");
            const resultado = await respuesta.json();

            select_busqueda_pnf.innerHTML = "<option value='' selected>Seleccionar el P.N.F</option>";

            resultado.nucleos.forEach(nucleo => {
                nucleo.pnfs.forEach(pnf => {
                    const option = document.createElement("option");
                    option.value = pnf.id_pnf;
                    option.textContent = pnf.pnf;
                    select_busqueda_pnf.appendChild(option);
                });
            });
        } catch (error) {
            console.error(error)
        }
    }
    pnfs_registrados();

    async function materias_registradas() {
        try {
            const formulario = new FormData();
            formulario.append("pnf", select_busqueda_pnf.value);
  
            const respuesta = await fetch("/mat_lista/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            contenedor_materias.innerHTML = "";

            const materiasPorPNF = {};
            resultado.pnfs.forEach(pnf => {
                materiasPorPNF[pnf.id_pnf] = {
                    id: pnf.id_pnf,
                    nombre: pnf.pnf,
                    codigo: pnf.codigo,
                    materias: []
                };
            });

            resultado.materias.forEach(materia => {
                if (materiasPorPNF[materia.id_pnf]) {
                    materiasPorPNF[materia.id_pnf].materias.push(materia);
                }
            });

            Object.values(materiasPorPNF).forEach(pnf => {
                if (pnf.materias.length === 0) return;

                const tabla = document.createElement("table");
                tabla.classList.add("tabla_materias");

                let filas = "";
                pnf.materias.forEach((materia, index) => {
                    filas += `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${materia.nombre}</td>
                            <td>${materia.codigo}</td>
                            <td>${materia.htea}</td>
                            <td>${materia.htei}</td>
                            <td>${materia.trayecto}</td>
                            <td>${materia.recuperacion}</td>
                        </tr>
                    `;
                });

                tabla.innerHTML = `
                    <thead>
                        <tr>
                            <th colspan="6">${pnf.nombre}</th>
                        </tr>
                        <tr>
                            <th>ID</th>
                            <th>Materia</th>
                            <th>Código</th>
                            <th>HTEA</th>
                            <th>HTEI</th>
                            <th>Trayecto</th>
                            <th>Recuperación</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filas}
                    </tbody>
                `;
                contenedor_materias.appendChild(tabla);
            });

        } catch (error) {
            console.error(error);
        }
    }
    materias_registradas();
    select_busqueda_pnf.addEventListener("change", materias_registradas);
});