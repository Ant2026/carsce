document.addEventListener("DOMContentLoaded", () => {

    const btn_discapacidad = document.getElementById("btn_discapacidad");
    const campos_discapacidad = document.getElementById("campos_discapacidad");

    const formulario_registro = document.getElementById("formulario_registro");

    // Campos registrado por el director general
    const nombres_usuario = document.getElementById("nombres_usuario");
    const apellidos_usuario = document.getElementById("apellidos_usuario");
    const CI_usuario = document.getElementById("CI");
    const genero_usuario = document.getElementById("genero_usuario");
    const estado_civil_usuario = document.getElementById("estado_civil_usuario");
    
    // Campos que puede ser que el director lo regitra o no del usuario
    const prefijo_principal = document.getElementById("prefijo_principal");
    const numero_telefonico_principal = document.getElementById("numero_telefonico_principal");
    
    const correo_principal = document.getElementById("correo_principal");
    const dominio_principal = document.getElementById("dominio_principal");

    const pais_profesion = document.getElementById("pais_profesion");

    const genero = ["Masculino", "Femenino"];
    const estado_civil = ["Soltero", "Casado", "Divorsiado", "Viudo"];

    // Controles para validar
    const nacionalidad_auxiliar = document.getElementById("nacionalidad_auxiliar");
    const cedula_auxiliar = document.getElementById("cedula_auxiliar");

    const prefijo_secundario = document.getElementById("prefijo_secundario");
    const numero_telefonico_secundario = document.getElementById("numero_telefonico_secundario");

    const prefijo_telefono_auxiliar = document.getElementById("prefijo_telefono_auxiliar");
    const numero_telefono_auxiliar = document.getElementById("numero_telefono_auxiliar");

    const correo_secundario = document.getElementById("correo_secundario");
    const dominio_secundario = document.getElementById("dominio_secundario");
    
    const fecha_grado = document.getElementById("fecha_grado");
    const codigo_sin_opsu = document.getElementById("codigo_sin_opsu");
    const discapacidad = document.getElementById("btn_discapacidad");

    const btn_registro = document.getElementById("btn_registro");

    const nucleos = document.querySelectorAll("#contenedor_pnfs_cursar input[type='checkbox']");

    // Mensaje de validar
    const msg_ced_aux = document.getElementById("msg_ced_aux");
    const msg_correo_princ = document.getElementById("msg_correo_princ");
    const msg_correo_sec = document.getElementById("msg_correo_sec");
    const msg_codigo_opsu = document.getElementById("msg_codigo_opsu");

    function opciones_select() {
        genero_usuario.innerHTML = "<option value='' selected>Selecciona una opción</option>";

        genero.forEach(genero => {
            const option = document.createElement("option");
            option.value = genero;
            option.textContent = genero;
            genero_usuario.append(option);
        });

        estado_civil_usuario.innerHTML = "<option value='' selected>Selecciona una opción</option>";

        estado_civil.forEach(estado_civil => {
            const option = document.createElement("option");
            option.value = estado_civil;
            option.textContent = estado_civil;
            estado_civil_usuario.append(option);
        });
    }
    opciones_select();
    
    async function datos_registrado() {
        try {
            const respuesta = await fetch("/datos_usr_admin/");
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado == "no_exite") {
                await Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                window.location.href = resultado.url;
            }

            nombres_usuario.value = resultado.usuario.nombres;
            apellidos_usuario.value = resultado.usuario.apellidos;
            CI_usuario.value = resultado.usuario.cedula_identidad;

            if (resultado.usuario.genero) {
                genero_usuario.classList.add("no-interaccion");

                const option_genero = document.createElement("option");
                option_genero.value = resultado.usuario.genero;
                option_genero.textContent = resultado.usuario.genero;
                option_genero.selected = true;
                option_genero.hidden = true;
                genero_usuario.append(option_genero);
            } else {
                genero_usuario.classList.remove("no-interaccion");
            }
            
            if (resultado.usuario.estado_civil) {
                estado_civil_usuario.classList.add("no-interaccion");

                const option_civil = document.createElement("option");
                option_civil.value = resultado.usuario.estado_civil;
                option_civil.textContent = resultado.usuario.estado_civil;
                option_civil.selected = true;
                option_civil.hidden = true;
                estado_civil_usuario.append(option_civil);
            } else {
                estado_civil_usuario.classList.remove("no-interaccion");
            }

            if (resultado.contacto.telefono_personal) {
                prefijo_principal.classList.add("no-interaccion");
                numero_telefonico_principal.readOnly = true;

                const prefijo_registrado = resultado.contacto.telefono_personal.slice(0, 4);
                const numero_telefonico = resultado.contacto.telefono_personal.slice(4, 11);

                const prefijo = document.createElement("option");
                prefijo.value = prefijo_registrado;
                prefijo.textContent = prefijo_registrado;
                prefijo.selected = true;
                prefijo.hidden = true;
                prefijo_principal.append(prefijo);

                numero_telefonico_principal.value = numero_telefonico;
            } else {
                numero_telefonico_principal.readOnly = false;
                prefijo_principal.classList.remove("no-interaccion");
            }

            if (resultado.contacto.correo_electronico) {
                correo_principal.readOnly = true;
                dominio_principal.classList.add("no-interaccion");

                const [nombre_correo, dominio_correo] = resultado.contacto.correo_electronico.split("@");

                correo_principal.value = nombre_correo;

                const dominio = document.createElement("option");
                dominio.value = "@" + dominio_correo;
                dominio.textContent = "@" + dominio_correo;
                dominio.selected = true;
                dominio.hidden = true;
                dominio_principal.append(dominio);
            } else {
                correo_principal.readOnly = false;
                dominio_principal.classList.remove("no-interaccion");
            }
   
        } catch (error) {
            console.error(error);
        }
    }
    datos_registrado();

    // Función para validar los controles
    if (nacionalidad_auxiliar && cedula_auxiliar && fecha_grado) {
        configurarCedula(nacionalidad_auxiliar, cedula_auxiliar);
        configurarFechaGrado(fecha_grado, 1);
    }

    configurarCorreo(correo_principal, dominio_principal);
    configurarCorreo(correo_secundario, dominio_secundario);

    configurarTelefono(numero_telefonico_principal, prefijo_principal);
    configurarTelefono(numero_telefonico_secundario, prefijo_secundario);

    if (prefijo_telefono_auxiliar && numero_telefono_auxiliar) {
        configurarTelefono(numero_telefono_auxiliar, prefijo_telefono_auxiliar);
    }

    if (pais_profesion) {
        cargarPaises(pais_profesion);
    }

    async function validar_cedula_auxiliar(nacionalidad_auxiliar, cedula_auxiliar) {
        try {
            const formulario = new FormData();
            formulario.append("nacionalidad", nacionalidad_auxiliar.value);
            formulario.append("cedula", cedula_auxiliar.value);

            const respuesta = await fetch("/validar_ci_auxiliar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario_registro
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.existe) {
                cedula_auxiliar.setCustomValidity("Ya existe un usuario con esta cedula de identidad.");
                cedula_auxiliar.classList.add("is-invalid");
                cedula_auxiliar.classList.remove("is-valid");

                msg_ced_aux.textContent = "Ya existe un usuario con esta cedula de identidad.";
                msg_ced_aux.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                cedula_auxiliar.setCustomValidity("");
                cedula_auxiliar.classList.add("is-valid");
                cedula_auxiliar.classList.remove("is-invalid");

                msg_ced_aux.textContent = "La cedula de identidad está disponible.";
                msg_ced_aux.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    function limpiarMensajeCedula() {
        if (msg_ced_aux) {
            msg_ced_aux.textContent = "";
            msg_ced_aux.className = "";
            cedula_auxiliar.style.border = "#000";
        }
    }

    if (nacionalidad_auxiliar) {
        nacionalidad_auxiliar.addEventListener("change", async () => {
            
            limpiarMensajeCedula();

            if (cedula_auxiliar.value.trim() !== "") {
                await validar_cedula_auxiliar(nacionalidad_auxiliar, cedula_auxiliar);
            }
        });
    }

    if (cedula_auxiliar) {
        cedula_auxiliar.addEventListener("input", async () => {

            if (cedula_auxiliar.value.trim() === "") {
                limpiarMensajeCedula();
                return;
            }

            validar_cedula_auxiliar(nacionalidad_auxiliar, cedula_auxiliar);
        });
    }

    async function validar_correos(correo, dominio, msg) {
        try {
            const formulario = new FormData();
            formulario.append("correo", correo.value);
            formulario.append("dominio", dominio.value);

            const respuesta = await fetch("/validar_email/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.existe) {
                correo.setCustomValidity("Ya existe un usuario con este correo electrónico.");
                correo.classList.add("is-invalid");
                correo.classList.remove("is-valid");

                msg.textContent = "Ya existe un usuario con este correo electrónico.";
                msg.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                correo.setCustomValidity("");
                correo.classList.add("is-valid");
                correo.classList.remove("is-invalid");

                msg.textContent = "El correo electrónico está disponible.";
                msg.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    correo_secundario.addEventListener("input", async () => {
        validar_correos(correo_secundario, dominio_secundario, msg_correo_sec);
    });

    dominio_secundario.addEventListener("change", async () => {
        validar_correos(correo_secundario, dominio_secundario, msg_correo_sec);
    });

    correo_principal.addEventListener("input", async () => {
        validar_correos(correo_principal, dominio_principal, msg_correo_princ);
    });

    dominio_principal.addEventListener("change", async () => {
        validar_correos(correo_principal, dominio_principal, msg_correo_princ);
    });

    async function codigo_opsu() {
        try {
            const formulario = new FormData();
            formulario.append("codigo", codigo_sin_opsu.value)
            
            const respuesta = await fetch("/validar_cod_opsu/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
        
            if (resultado.existe) {
                codigo_sin_opsu.setCustomValidity("Ya se encuentra un estudiante con el mismo código OPSU.");
                codigo_sin_opsu.classList.add("is-invalid");
                codigo_sin_opsu.classList.remove("is-valid");

                msg_codigo_opsu.textContent = "Ya se encuentra un estudiante con el mismo código OPSU.";
                msg_codigo_opsu.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                codigo_sin_opsu.setCustomValidity("");
                codigo_sin_opsu.classList.add("is-valid");
                codigo_sin_opsu.classList.remove("is-invalid");

                msg_codigo_opsu.textContent = "Código OPSU se encuentra disponible.";
                msg_codigo_opsu.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }
    
    if (codigo_sin_opsu) {
        codigo_sin_opsu.addEventListener("input", codigo_opsu);

        codigo_sin_opsu.addEventListener("keypress", function (e) {
            if (!/[0-9]/.test(e.key)) {
                e.preventDefault();
            }
        });
    }

    formulario_registro.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registro);

            const respuesta = await fetch("/comp_registro/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                title: resultado.title,
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
            
            if (resultado.estado == "exito") {
                window.location.href = resultado.url;
            }
        } catch (error) {
            console.error(error);
        }
    });

    if (discapacidad) {
        // Ocultar o visualizar los campos visualizar
        discapacidad.addEventListener("click", () => {
            campos_discapacidad.classList.toggle("activo");

            if (campos_discapacidad.classList.contains("activo")) {
                discapacidad.textContent = "Ocultar";
            } else {
                discapacidad.textContent = "Mostrar";
            }
        });
    }
     
    nucleos.forEach(nucleo => {
        nucleo.addEventListener("change", async function () {
            const contenedor = document.getElementById(`contenedor_pnfs_${this.value}`);
            console.log("Contenedor:", contenedor);

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

            const respuesta = await fetch("/pnfs_cursar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            const contenedor = document.getElementById(`contenedor_pnfs_${nucleo}`);

            contenedor.innerHTML = "";
            resultado.pnfs.forEach(pnf => {
                contenedor.innerHTML += `
                    <label>${pnf.nombre}
                        <input type="checkbox" value="${pnf.id}" name="pnf_${nucleo}">
                    </label>
                `;
            });

        } catch (error) {
            console.error(error);
        }
    }
});