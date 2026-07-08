document.addEventListener("DOMContentLoaded", () => {

    const formulario_actualizar = document.getElementById("formulario_actualizar")

    const select_prefijo_principal = document.getElementById("prefijo_telefono2")
    const input_telefono_principal = document.getElementById("numero_telefonico2")
    const select_prefijo_secundaria = document.getElementById("prefijo_telefono3")
    const input_telefono_secundaria = document.getElementById("numero_telefonico3")

    const input_correo_principal = document.getElementById("Correo_num2")
    const select_dominio_principal = document.getElementById("dominio_num2")
    const input_correo_secundario = document.getElementById("Correo_num3")
    const select_dominio_secundario = document.getElementById("dominio_num3")
    
    const select_condicion_residencia = document.getElementById("condicion_residencia")
    const select_municipio_residencia = document.getElementById("municipio_residencia")
    const select_parroquia_residencia = document.getElementById("parroquia_residencia")
    const textarea_direccion_domicilio = document.getElementById("direccion_domicilio")

    const input_codigo_carnet = document.getElementById("codigo_carnet_dispacidad")
    const input_nro_registro_medico = document.getElementById("nro_registro_medico")
    const select_tipos_discapacidad = document.getElementById("tipos_discapacidad")
    const select_grado_discapacidad = document.getElementById("grado_discapacidad")
    const select_causa_discapacidad = document.getElementById("causa_discapacidad")

    const dialogo_actualizar_correo = document.getElementById("menu_actualizar_correo")
    const btn_cerrar_dialogo = document.getElementById("cerrar_dialogo_correo")
    const formulario_seleccionar_correo = document.getElementById("formulario_correos")

    const dialogo_autentica_codigo = document.getElementById("autenticacion_correo")
    const formulario_autenticacion = document.getElementById("formulario_autenticacion")
    const btn_reenviar_codigo = document.getElementById("btn_reenviar_codigo")
    const contador_reenvio = document.getElementById("contador_reenvio")

    const label_correo_principal = document.getElementById("label_correo_principal")
    const label_correo_secundario = document.getElementById("label_correo_secundario")
    const input_check_correo_principal = document.getElementById("correo_principal")
    const input_check_correo_secundario = document.getElementById("correo_principal")

    let datosPendientes = null;

    async function datos_usuario() {
        try {
            const respuesta = await fetch("/datos_usuario/")
            const resultado = await respuesta.json()

            const telefonoPrincipal = resultado.contacto.telefono_personal;
            const prefijoPrincipal = telefonoPrincipal.substring(0, 4);
            const numeroPrincipal = telefonoPrincipal.substring(4);
            
            const option_tlf1 = document.createElement("option")
            option_tlf1.value = prefijoPrincipal
            option_tlf1.textContent = prefijoPrincipal
            option_tlf1.selected = true
            option_tlf1.hidden = true
            select_prefijo_principal.append(option_tlf1)

            input_telefono_principal.value = numeroPrincipal
    
            const telefonoSecundario = resultado.contacto.telefono_suplete;
            const prefijoSecundario = telefonoSecundario.substring(0, 4);
            const numeroSecundario = telefonoSecundario.substring(4);

            const option_tlf2 = document.createElement("option");
            option_tlf2.value = (prefijoSecundario === "N/A") ? "" : prefijoSecundario;
            option_tlf2.textContent = (prefijoSecundario === "N/A") ? "TLF" : prefijoSecundario;
            option_tlf2.selected = true;
            option_tlf2.hidden = true;
            select_prefijo_secundaria.append(option_tlf2);

            if (numeroSecundario === "") {
                input_telefono_secundaria.value = "";
                input_telefono_secundaria.placeholder = "Ingrese un número de teléfono secundario";
            } else {
                input_telefono_secundaria.value = numeroSecundario;
                input_telefono_secundaria.placeholder = "";
            }

            const correoPrincipal = resultado.contacto.correo_electronico;

            const [usuarioCorreoPrincipal, dominioPrincipal] = correoPrincipal.split("@");

            input_correo_principal.value = usuarioCorreoPrincipal

            const option_dominio = document.createElement("option")
            option_dominio.value = "@" + dominioPrincipal
            option_dominio.textContent = "@" + dominioPrincipal
            option_dominio.selected = true
            option_dominio.hidden = true
            select_dominio_principal.append(option_dominio)

            const correoSecundario = resultado.contacto.correo_alternativo;
            if (correoSecundario) {
                const [usuarioCorreoSecundario, dominioSecundario] = correoSecundario.split("@");

                input_correo_secundario.value = usuarioCorreoSecundario

                const option_dominio = document.createElement("option")
                option_dominio.value = "@" + dominioSecundario
                option_dominio.textContent = "@" + dominioSecundario
                option_dominio.selected = true
                option_dominio.hidden = true
                select_dominio_secundario.append(option_dominio)
            }

            const option_condicion_residencia = document.createElement("option")
            option_condicion_residencia.value = resultado.residencia.condicion_residencia
            option_condicion_residencia.textContent = resultado.residencia.condicion_residencia
            option_condicion_residencia.selected = true
            option_condicion_residencia.hidden = true
            select_condicion_residencia.append(option_condicion_residencia)
            
            const option_municipio_residencia = document.createElement("option")
            option_municipio_residencia.value = resultado.residencia.municipio
            option_municipio_residencia.textContent = resultado.residencia.municipio
            option_municipio_residencia.selected = true
            option_municipio_residencia.hidden = true
            select_municipio_residencia.append(option_municipio_residencia)
            
            const option_parroquia_residencia = document.createElement("option")
            option_parroquia_residencia.value = resultado.residencia.parroquia
            option_parroquia_residencia.textContent = resultado.residencia.parroquia
            option_parroquia_residencia.selected = true
            option_parroquia_residencia.hidden = true
            select_parroquia_residencia.append(option_parroquia_residencia)

            textarea_direccion_domicilio.value = resultado.residencia.direccion_residencia

            if (resultado.discapacidad) {
                input_codigo_carnet.value = resultado.discapacidad.codigo_carnet_discapacidad
                input_nro_registro_medico.value = resultado.discapacidad.nro_registro_medico

                const option_tipos_discapacidad = document.createElement("option")
                option_tipos_discapacidad.value = resultado.discapacidad.tipo_discapacidad
                option_tipos_discapacidad.textContent = resultado.discapacidad.tipo_discapacidad
                option_tipos_discapacidad.selected = true
                option_tipos_discapacidad.hidden = true
                select_tipos_discapacidad.append(option_tipos_discapacidad)
                
                const option_grado_discapacidad = document.createElement("option")
                option_grado_discapacidad.value = resultado.discapacidad.grado_discapacidad
                option_grado_discapacidad.textContent = resultado.discapacidad.grado_discapacidad
                option_grado_discapacidad.selected = true
                option_grado_discapacidad.hidden = true
                select_grado_discapacidad.append(option_grado_discapacidad)
                
                const option_causa_discapacidad = document.createElement("option")
                option_causa_discapacidad.value = resultado.discapacidad.causa_discapacidad
                option_causa_discapacidad.textContent = resultado.discapacidad.causa_discapacidad
                option_causa_discapacidad.selected = true
                option_causa_discapacidad.hidden = true
                select_causa_discapacidad.append(option_causa_discapacidad)
            }
        } catch (error) {
            console.error(error)
        }
    }
    datos_usuario();

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const respuesta = await fetch("/correos_usuario/");
            const resultado = await respuesta.json();

            const correoPrincipalNuevo = input_correo_principal.value.trim() + select_dominio_principal.value;
            const correoAlternativoNuevo = input_correo_secundario.value.trim() + select_dominio_secundario.value;

            const cambioCorreo =
                correoPrincipalNuevo !== resultado.correo_principal ||
                correoAlternativoNuevo !== resultado.correo_alternativo;

            if (cambioCorreo) {

                label_correo_principal.textContent = resultado.correo_principal;

                if (resultado.correo_alternativo) {
                    label_correo_secundario.textContent = resultado.correo_alternativo;
                    document.querySelector(".opcion_correo:nth-child(2)").style.display = "flex";
                } else {
                    document.querySelector(".opcion_correo:nth-child(2)").style.display = "none";
                }

                dialogo_actualizar_correo.showModal();
                return;
            }

            await actualizarDatos();
        } catch (error) {
            console.error(error);
        }
    });

    formulario_seleccionar_correo.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_seleccionar_correo)

            const respuesta = await fetch("/enviar_codigo_actualizar_correo/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json()
            

            dialogo_autentica_codigo.showModal()
            dialogo_actualizar_correo.close()
        } catch (error) {
            console.error(error)
        }
    });

    async function actualizarDatos() {
        try {
            const respuesta = await fetch("/actualizar_datosusuario/", {
                method: "POST",
                body: new FormData(formulario_actualizar)
            });
            const resultado = await respuesta.json();

            await datos_usuario();
            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
        } catch (error) {
            console.error(error);
        }
    }

    formulario_autenticacion.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_autenticacion);

            const respuesta = await fetch("/autenticacion_actualizar_correo/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            if (resultado.estado == "exito") {
                dialogo_autentica_codigo.close();
                formulario_autenticacion.reset();

                await actualizarDatos();
       
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
        } catch (error) {
            console.error(error);
        }
    });

    btn_cerrar_dialogo.addEventListener("click", () => {
        dialogo_actualizar_correo.close();
    });

    const DURACION = 60;

    function iniciarContador() {
        const inicio = localStorage.getItem("inicio_reenvio");
        if (!inicio) {
            btn_reenviar_codigo.disabled = false;
            return;
        }

        btn_reenviar_codigo.disabled = true;

        const intervalo = setInterval(() => {
            const transcurrido = Math.floor(
                (Date.now() - parseInt(inicio)) / 1000
            );
            const restante = DURACION - transcurrido;

            if (restante <= 0) {
                clearInterval(intervalo);
                btn_reenviar_codigo.disabled = false;
                contador_reenvio.textContent = "";
                localStorage.removeItem("inicio_reenvio");
                return;
            }
            contador_reenvio.textContent = restante;
        }, 1000);
    }
    iniciarContador();

    btn_reenviar_codigo.addEventListener("click", async (e) => {
        e.preventDefault()
        try {
            btn_reenviar_codigo.disabled = true;

            const respuesta = await fetch("/reenviar_codigo_btn/")
            const resultado = await respuesta.json()

            await Swal.fire({
                icon: resultado.icon || "info",
                text: resultado.descripcion
            });
        } catch (error) {
            console.error(error)
        }
    })
});