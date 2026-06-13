document.addEventListener("DOMContentLoaded", () => {   

    const formulario_buscar_usuario = document.getElementById("buscar_usuario")
    const formulario_registrar_credenciales = document.getElementById("formulario_registrar_credenciales")

    const label_CI = document.getElementById("label_CI")
    const select_nacionalidad = document.getElementById("nacionalidad")
    const input_CI = document.getElementById("cedula_identidad")
    const btn_buscar_usuario = document.getElementById("comprobar_usuario")

    const label_nombre_usuario = document.getElementById("label_nombre_usuario")
    const label_password = document.getElementById("label_password")
    const input_nombre_usuario = document.getElementById("nombre_usuario")
    const input_password = document.getElementById("password")
    const btn_guardar_credenciales = document.getElementById("guardar_credenciales")

    const tag_i_mostrar = document.getElementById("mostrar_password")
    const tag_i_ocultar = document.getElementById("ocultar_password")

    const contenedor_validar = document.getElementById("bar_contrasenia")

    formulario_buscar_usuario.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const datos = new FormData(formulario_buscar_usuario);

            const respuesta = await fetch("/confirmar_registro_personal/", {
                method: "POST",
                body: datos,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            });
            const resultado = await respuesta.json()
            
            if (resultado.existe == "success") {
                label_CI.hidden = true
                select_nacionalidad.hidden = true
                input_CI.hidden = true
                btn_buscar_usuario.hidden = true
                
                label_nombre_usuario.hidden = false
                label_password.hidden = false
                input_nombre_usuario.hidden = false
                input_password.hidden = false
                btn_guardar_credenciales.hidden = false

                contenedor_validar.hidden = false

                tag_i_mostrar.hidden = false
                tag_i_ocultar.hidden = false
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }

            formulario_buscar_usuario.reset()
        } catch (error) {
            Swal.fire({
                title: "Error",
                text: error,
                icon: "error",
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        }
    });

    formulario_registrar_credenciales.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const datos = new FormData(formulario_registrar_credenciales);

            const respuesta = await fetch("/guardar_credenciales_personal/", {
                method: "POST",
                body: datos,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            });
            const resultado = await respuesta.json()
            
            if (resultado.existe == "success") {
                if (resultado.existe == "success") {

                    await Swal.fire({
                        text: resultado.descripcion,
                        icon: resultado.icon,
                        allowOutsideClick: false,
                        allowEscapeKey: false
                    });

                    label_CI.hidden = false
                    select_nacionalidad.hidden = false
                    input_CI.hidden = false
                    btn_buscar_usuario.hidden = false
                    
                    label_nombre_usuario.hidden = true
                    label_password.hidden = true
                    input_nombre_usuario.hidden = true
                    input_password.hidden = true
                    btn_guardar_credenciales.hidden = true
                    contenedor_validar.hidden = true
                    tag_i_mostrar.hidden = true
                    tag_i_ocultar.hidden = true
                }
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }

            
            formulario_registrar_credenciales.reset()
        } catch (error) {
            Swal.fire({
                title: "Error",
                text: error,
                icon: "error",
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        }
    })

});