document.addEventListener("DOMContentLoaded", () => {
    const formulario_estudiante = document.getElementById("formulario_pe")
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const nucleos = document.querySelectorAll("#contenedor_PE_Cursar input[type='checkbox']");

    formulario_estudiante.addEventListener("submit", async function (e) {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_estudiante);

            const respuesta = await fetch("/completar_registro_pe/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            Swal.fire({
                title: resultado.titulo,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado === "exito") {
                window.location.href = "/panel_usuario/";
            }
        } catch (error) {
            console.error(error);
        }
    });

    nucleos.forEach(nucleo => {
        nucleo.addEventListener("change", async function () {
            const contenedor = document.getElementById(`contenedor_pnfs_${this.value}`);
            if (!this.checked) {
                if (contenedor) {
                    contenedor.innerHTML = "";
                }
                return;
            }
            await cursarpnfs(this.value);
        });
    });

    async function cursarpnfs(nucleo) {
        try {
            const formulario = new FormData();
            formulario.append("nucleo", nucleo);

            const respuesta = await fetch("/mostrar_pnfs_cursar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            const contenedor = document.getElementById(`contenedor_pnfs_${nucleo}`);

            contenedor.innerHTML = "";
            resultado.pnfs.forEach(pnf => {
                contenedor.innerHTML += `
                    <label>
                        ${pnf.nombre}
                        <input
                            type="checkbox"
                            value="${pnf.id}"
                            name="pnf_${nucleo}"
                        >
                    </label>
                `;
            });
        } catch (error) {
            console.error(error);
        }
    }
});