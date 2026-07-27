document.addEventListener("DOMContentLoaded", () => {   

    // Identificadores de los formularios
    const formulario_buscar_usuario = document.getElementById("buscar_usuario");
    const formulario_registrar_credenciales = document.getElementById("formulario_registrar_credenciales");

    // Controles para la busqueda del usuario
    const titulo_busqueda = document.getElementById("titulo_busqueda");
    const label_CI = document.getElementById("label_CI");
    const select_nacionalidad = document.getElementById("nacionalidad");
    const input_CI = document.getElementById("cedula_identidad");
    const btn_buscar_usuario = document.getElementById("validar_usuario");

    // Registrar sus credenciales
    const titulo_guardar = document.getElementById("titulo_guardar");
    const label_nombre_usuario = document.getElementById("label_nombre_usuario");
    const label_password = document.getElementById("label_password");
    const input_nombre_usuario = document.getElementById("nombre_usuario");
    const input_password = document.getElementById("password");
    const btn_guardar_credenciales = document.getElementById("guardar_credenciales");

    // Botones para ocultar o mostrar la contraseña
    const tag_i_mostrar = document.getElementById("mostrar_password");
    const tag_i_ocultar = document.getElementById("ocultar_password");

    const busqueda_usuario = [
        titulo_busqueda,
        label_CI,
        select_nacionalidad,
        input_CI,
        btn_buscar_usuario
    ]

    function ocultar_busqueda(ocultar = true) {
        busqueda_usuario.forEach(control => {
            if (control) {
                control.hidden = ocultar;
            }
        });
    }

    const registrar_credenciales = [
        titulo_guardar,
        label_nombre_usuario,
        label_password,
        input_nombre_usuario,
        input_password,
        btn_guardar_credenciales,
        tag_i_mostrar,
        tag_i_ocultar
    ]

    function ocultar_credenciales(ocultar = true) {
        registrar_credenciales.forEach(control => {
            if (control) {
                control.hidden = ocultar;
            }
        });
    }

    ocultar_credenciales(true);

    formulario_buscar_usuario.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const datos = new FormData(formulario_buscar_usuario);

            const respuesta = await fetch("/confirmar_registro_personal/", {
                method: "POST",
                body: datos
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado == "exito") {
                ocultar_busqueda(true);
                ocultar_credenciales(false);
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
            console.error(error);
        }
    });

    formulario_registrar_credenciales.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const datos = new FormData(formulario_registrar_credenciales);

            const respuesta = await fetch("/guardar_credenciales_personal/", {
                method: "POST",
                body: datos
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.estado == "exito") {
                ocultar_busqueda(false);
                ocultar_credenciales(true);
            }

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
            
            formulario_registrar_credenciales.reset()
        } catch (error) {
            console.error(error)
        }
    });
});