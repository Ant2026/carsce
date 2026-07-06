document.addEventListener("DOMContentLoaded", () => {
    const nombres_registrado = document.getElementById("nombres_usuario")
    const apellidos_registrado = document.getElementById("apellidos_usuario")
    const cedula_identidad_registrado = document.getElementById("CI")

    const telefono_principal_registrado = document.getElementById("telefono_principal_usuario")
    const correo_principal_registrado = document.getElementById("correo_principal_usuario")

    const formulario_estudiante = document.getElementById("formulario_CRE")

    async function datos_registrado() {
        try {
            const respuesta = await fetch("/datos_registrado/")
            const resultado = await respuesta.json()

            nombres_registrado.value = resultado.usuario.nombres
            apellidos_registrado.value = resultado.usuario.apellidos
            cedula_identidad_registrado.value = resultado.usuario.cedula_identidad

            telefono_principal_registrado.value = resultado.contacto.telefono_personal
            correo_principal_registrado.value = resultado.contacto.correo_electronico
        } catch (error) {
            console.error(error)
        }
    }
    datos_registrado()

    formulario_estudiante.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const respuesta = await fetch("/completar_registro_estudiante/", {
                method: "POST",
                body: new FormData(formulario_estudiante)
            });
            const resultado = await respuesta.json()
            console.log(resultado)
            if (resultado.estado === "success") {
                window.location.href = "/panel_usuario/";
            } else {
                Swal.fire({
                    title: resultado.titulo,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
        } catch (error) {
            console.error(error)
        }
    });

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const nucleos = document.querySelectorAll("#contenedor_CRE_Cursar input[type='checkbox']");

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
            const datos = new FormData();
            datos.append("nucleo", nucleo);

            const respuesta = await fetch("/mostrar_pnfs_cursar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: datos
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
                    </label>`;
            });
        } catch (error) {
            console.error(error);
        }
    }
});