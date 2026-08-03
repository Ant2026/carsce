document.addEventListener("DOMContentLoaded", () => {

    const formulario_actualizar = document.getElementById("formulario_actualizar");
    const contenedor_autoridades = document.getElementById("contenedor_autoridades");
    const btn_actualizar = document.getElementById("btn_actualizar");

    const cargos = [
        "Rector",
        "Vicerrector",
        "Responsable Académico"
    ];

    async function autoridades_registradas() {
        try {
            const respuesta = await fetch("/auts_reg/");
            const resultado = await respuesta.json();

            let tabla = "";
            resultado.forEach(usuario => {
                tabla += `
                    <tr>
                        <td>${usuario.nombres}</td>
                        <td>${usuario.apellidos}</td>
                        <td>${usuario.cedula_identidad}</td>
                        <td>${usuario.cargo}</td>

                        <td>
                            <select class="select_cargo" 
                                name="cargo_${usuario.id_autoridad}" 
                                data-id="${usuario.id_autoridad}">
                `;

                cargos.forEach(cargo => {
                    tabla += `
                        <option value="${cargo}"
                            ${cargo === usuario.cargo ? "selected" : ""}>
                            ${cargo}
                        </option>
                    `;
                });

                tabla += `
                            </select>
                        </td>
                    </tr>
                `;
            });

            contenedor_autoridades.innerHTML = tabla;

            document.querySelectorAll(".select_cargo").forEach(select => {

                select.addEventListener("change", function () {

                    let cargoSeleccionado = this.value;

                    document.querySelectorAll(".select_cargo").forEach(otroSelect => {

                        // No comparar contra el mismo select
                        if (otroSelect !== this) {
                            if (otroSelect.value === cargoSeleccionado) {
                                otroSelect.value = "";
                            }
                        }
                    });
                });
            });
        } catch (error) {
            console.error(error);
        }
    }
    autoridades_registradas();

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault();
        const select = e.target.closest("form").querySelector("select");
        console.log(select);

        try {
            const formulario = new FormData(formulario_actualizar);

            formulario.append("id_autoridad", select.dataset.id);

            const respuesta = await fetch("/reasig_cargo/", {
                method: "POST",
                body: formulario
            });

            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        } catch (error) {
            console.error(error);
        }
    });
});