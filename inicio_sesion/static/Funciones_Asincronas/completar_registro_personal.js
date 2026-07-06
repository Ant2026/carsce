document.addEventListener("DOMContentLoaded", () => {
    const nombres_registrado = document.getElementById("nombres_usuario")
    const apellidos_registrado = document.getElementById("apellidos_usuario")
    const cedula_identidad_registrado = document.getElementById("CI")

    const telefono_principal_registrado = document.getElementById("telefono_principal_usuario")
    const correo_principal_registrado = document.getElementById("correo_principal_usuario")

    const formulario_personal = document.getElementById("formulario_CRP")

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

    formulario_personal.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const respuesta = await fetch("/completar_registro_personal/", {
                method: "POST",
                body: new FormData(formulario_personal)
            });
            const resultado = await respuesta.json()

            if (resultado.estado === "success") {
                Swal.fire({
                    title: "Éxito",
                    text: "Los datos se registraron exitosamente",
                    icon: "success",
                    allowOutsideClick: false,
                    allowEscapeKey: false
                }).then(() => {
                    window.location.href = "/panel_usuario/";
                });
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
});