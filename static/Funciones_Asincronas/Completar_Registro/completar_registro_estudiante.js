document.addEventListener("DOMContentLoaded", () => {
    const nombres_registrado = document.getElementById("nombres_usuario")
    const apellidos_registrado = document.getElementById("apellidos_usuario")
    const cedula_identidad_registrado = document.getElementById("CI")
    const telefono_principal_registrado = document.getElementById("telefono_principal_usuario")
    const correo_principal_registrado = document.getElementById("correo_principal_usuario")

    const nacionalidad_representante_principal = document.getElementById("nacionalidad2");
    const cedula_identidad1_representante_principal = document.getElementById("cedula_identidad2");
    const mensaje_cedula_respresentante_principal = document.getElementById("mensaje_cedula_respresentante_principal");
    
    const nacionalidad_representante_secundario = document.getElementById("nacionalidad3");
    const cedula_identidad2_representante_secundario = document.getElementById("cedula_identidad3");
    const mensaje_cedula_respresentante_secundario = document.getElementById("mensaje_cedula_respresentante_secundario");

    const input_correo_secundario = document.getElementById("Correo");
    const select_dominio = document.getElementById("dominio");
    const mensaje_correo_electronico = document.getElementById("mensaje_correo_electronico");

    const input_codigo_sin_opsu = document.getElementById("codigo_sin_opsu");
    const mensaje_codigo_opsu = document.getElementById("mensaje_codigo_opsu");

    const btn_registro = document.getElementById("btn_registro");

    const formulario_estudiante = document.getElementById("formulario_CRE")
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const nucleos = document.querySelectorAll("#contenedor_CRE_Cursar input[type='checkbox']");

    async function datos_registrado() {
        try {
            const respuesta = await fetch("/datos_registrado/");
            const resultado = await respuesta.json();

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

    async function validarCorreo(inputCorreo, selectDominio, mensaje) {
        const correo = inputCorreo.value.trim();
        const dominio = selectDominio.value;

        if (correo === "") {
            inputCorreo.setCustomValidity("");
            inputCorreo.classList.remove("is-valid", "is-invalid");
            mensaje.textContent = "";
            return;
        }

        if (dominio === "" || correo.length < 10 || correo.length > 30) {
            return;
        }

        try {
            const formulario = new FormData();
            formulario.append("correo", correo);
            formulario.append("dominio", dominio);

            const respuesta = await fetch("/verificar_correo_electronico/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            if (resultado.existe) {
                inputCorreo.setCustomValidity("Ya existe un usuario con este correo electrónico.");
                inputCorreo.classList.add("is-invalid");
                inputCorreo.classList.remove("is-valid");

                mensaje.textContent = "Ya existe un usuario con este correo electrónico.";
                mensaje.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                inputCorreo.setCustomValidity("");
                inputCorreo.classList.add("is-valid");
                inputCorreo.classList.remove("is-invalid");

                mensaje.textContent = "El correo electrónico está disponible.";
                mensaje.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }
    input_correo_secundario.addEventListener("input", () => {
        validarCorreo(input_correo_secundario, select_dominio, mensaje_correo_electronico);
    });
    select_dominio.addEventListener("change", () => {
        validarCorreo(input_correo_secundario, select_dominio, mensaje_correo_electronico);
    });

    async function validarCedula(selectNacionalidad, inputCedula, mensaje) {
        const nacionalidad = selectNacionalidad.value;
        const cedula = inputCedula.value.trim();

        if (cedula.length === 0) {
            mensaje.textContent = "";

            inputCedula.setCustomValidity("");

            inputCedula.classList.remove("is-valid", "is-invalid");

            btn_registro.disabled = false;
            return;
        }

        const valida =
            (nacionalidad === "V" && cedula.length >= 7 && cedula.length <= 8) ||
            (nacionalidad === "E" && cedula.length >= 8 && cedula.length <= 10);

        if (!valida) return;

        try {
            const formulario = new FormData();
            formulario.append("nacionalidad", nacionalidad);
            formulario.append("cedula", cedula);

            const respuesta = await fetch("/verificar_cedula_representante/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });

            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.existe) {
                inputCedula.setCustomValidity(
                    "Ya se encuentra un usuario registrado con esta cédula de identidad."
                );

                inputCedula.classList.add("is-invalid");
                inputCedula.classList.remove("is-valid");

                mensaje.textContent = "Ya se encuentra un usuario registrado con esta cédula de identidad.";
                mensaje.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                inputCedula.setCustomValidity("");

                inputCedula.classList.remove("is-invalid");
                inputCedula.classList.add("is-valid");

                mensaje.textContent = "La cédula de identidad está disponible.";
                mensaje.style.color = "#198754";

                btn_registro.disabled = false;
            }

        } catch (error) {
            console.error(error);
        }
    }

    nacionalidad_representante_principal.addEventListener("change", async () => {
        validarCedula(nacionalidad_representante_principal, cedula_identidad1_representante_principal, mensaje_cedula_respresentante_principal);
    });

    cedula_identidad1_representante_principal.addEventListener("input", async () => {
        validarCedula(nacionalidad_representante_principal, cedula_identidad1_representante_principal, mensaje_cedula_respresentante_principal);
    });

    nacionalidad_representante_secundario.addEventListener("change", async () => {
        validarCedula(nacionalidad_representante_secundario, cedula_identidad2_representante_secundario, mensaje_cedula_respresentante_secundario);
    });

    cedula_identidad2_representante_secundario.addEventListener("input", async () => {
        validarCedula(nacionalidad_representante_secundario, cedula_identidad2_representante_secundario, mensaje_cedula_respresentante_secundario);
    });

    async function codigo_opsu() {
        const codigo = input_codigo_sin_opsu.value;
        
        if (codigo.length === 0 || codigo.length <= 4) {
            mensaje_codigo_opsu.textContent = "";

            input_codigo_sin_opsu.setCustomValidity("");
            input_codigo_sin_opsu.classList.remove("is-valid");
            input_codigo_sin_opsu.classList.remove("is-invalid");
            return;
        }

        if (codigo.length >= 5 && codigo.length <= 5) {
            await buscar_codigo_opsu(codigo);
        }
    }
    input_codigo_sin_opsu.addEventListener("input", codigo_opsu);

    async function buscar_codigo_opsu(codigo) {
        try {
            const formulario = new FormData();
            formulario.append("codigo", codigo);

            const respuesta = await fetch("/verificar_codigo_opsu/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.existe == true) {
                input_codigo_sin_opsu.setCustomValidity("Ya se encuentra un usuario registrado con este nombre de usuario.");

                input_codigo_sin_opsu.classList.add("is-invalid");
                input_codigo_sin_opsu.classList.remove("is-valid");

                mensaje_codigo_opsu.textContent = "Ya se encuentra un usuario registrado con este nombre de usuario.";
                mensaje_codigo_opsu.style.color = "#dc3545";

                btn_registro.disabled = true;
            }

            if (resultado.existe == false) {
                input_codigo_sin_opsu.setCustomValidity("");

                input_codigo_sin_opsu.classList.remove("is-invalid");
                input_codigo_sin_opsu.classList.add("is-valid");

                mensaje_codigo_opsu.textContent = "El nombre de usuario está disponible.";
                mensaje_codigo_opsu.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }


    input_codigo_sin_opsu.addEventListener("keypress", function (e) {
        if (!/[0-9]/.test(e.key)) {
            e.preventDefault();
        }
    });

    formulario_estudiante.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_estudiante);

            const respuesta = await fetch("/completar_registro_estudiante/", {
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

            const respuesta = await fetch("/mostrar_pnfs_cursar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
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