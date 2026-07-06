document.addEventListener("DOMContentLoaded", () => {
    
    const formulario_actualizar_usuario = document.getElementById("formulario_actualizar_usuario");

    // Datos básicos
    const perfil_usuario = document.getElementById("perfil_usuario")
    const nombres_actualizar_usuario = document.getElementById("nombres_actualizar_usuario");
    const apellidos_actualizar_usuario = document.getElementById("apellidos_actualizar_usuario");
    const genero_actualizar_usuario = document.getElementById("genero_actualizar_usuario");
    const nacionalidad = document.getElementById("nacionalidad_actualizar_usuario");
    const cedula_identidad = document.getElementById("cedula_identidad_actualizar_usuario");
    const estado_civil_actualizar_usuario = document.getElementById("estado_civil_actualizar_usuario");

    // Contacto
    const prefijo_telefono_principal = document.getElementById("prefijo_telefono_principal_actualizar");
    const num_telefono_principal = document.getElementById("num_telefono_principal_actualizar");

    const prefijo_telefono_secundaria = document.getElementById("prefijo_telefono_secundaria_actualizar");
    const num_telefonico_secundaria = document.getElementById("num_telefonico_secundaria_actualizar");

    const correo_principal = document.getElementById("correo_principal_actualizar");
    const dominio_principal = document.getElementById("dominio_principal_actualizar");

    const correo_secundaria = document.getElementById("correo_secundaria_actualizar");
    const dominio_secundaria = document.getElementById("dominio_secundaria_actualizar");

    // Nacimiento
    const pais_nacimiento = document.getElementById("pais_nacimiento");
    const estado_nacimiento = document.getElementById("estado_nacimiento");
    const estado_novzla = document.getElementById("estado_novzla");
    const municipio_nacimiento = document.getElementById("municipio_nacimiento");
    const municipio_novzla = document.getElementById("municipio_novzla");
    const parroquia_nacimiento = document.getElementById("parroquia_nacimiento");
    const parroquia_novzla = document.getElementById("parroquia_novzla");
    const direccion_nacimiento = document.getElementById("direccion_nacimiento");
    const fecha_nacimiento = document.getElementById("fecha_nacimiento");

    // Residencia
    const condicion_residencia = document.getElementById("condicion_residencia");
    const municipio_residencia = document.getElementById("municipio_residencia");
    const parroquia_residencia = document.getElementById("parroquia_residencia");
    const direccion_domicilio = document.getElementById("direccion_domicilio");

    // Profesión
    const profesion_usuario = document.getElementById("profesion_usuario");
    const universidad_usuario = document.getElementById("universidad_usuario");
    const pais_profesion = document.getElementById("pais_profesion");

    // Secundaria
    const tipos_secundaria = document.getElementById("tipos_secundaria");
    const nombre_liceo = document.getElementById("nombre_liceo");
    const fecha_grado = document.getElementById("fecha_grado");
    const codigo_sin_opsu = document.getElementById("codigo_sin_opsu");

    // Representante
    const nombres_representante = document.getElementById("nombres_representante");
    const apellidos_representante = document.getElementById("apellidos_representante");
    const nacionalidad_representante = document.getElementById("nacionalidad_representante");
    const cedula_identidad_representante = document.getElementById("cedula_identidad_representante");
    const prefijo_telefono_representante = document.getElementById("prefijo_telefono_representante");
    const numero_telefono_representante = document.getElementById("numero_telefono_representante");
    const parestenco_representante = document.getElementById("parestenco_representante");
    const btn_otro_representante = document.getElementById("btn_otro_representante");
    const subcontenedor_representante = document.getElementById("subcontenedor_representante");

    // Segundo representante
    const nombres_otrorepresentante = document.getElementById("nombres_otrorepresentante");
    const apellidos_otrorepresentante = document.getElementById("apellidos_otrorepresentante");
    const nacionalidad_otrorepresentante = document.getElementById("nacionalidad_otrorepresentante");
    const cedula_identidad_otrorepresentante = document.getElementById("cedula_identidad_otrorepresentante");
    const prefijo_telefono_otrorepresentante = document.getElementById("prefijo_telefono_otrorepresentante");
    const numero_telefono_otrorepresentante = document.getElementById("numero_telefono_otrorepresentante");
    const otroparestenco = document.getElementById("otroparestenco");

    // Discapacidad
    const btn_discapacidad = document.getElementById("btn_discapacidad");
    const codigo_carnet_dispacidad = document.getElementById("codigo_carnet_dispacidad");
    const nro_registro_medico = document.getElementById("nro_registro_medico");
    const tipos_discapacidad = document.getElementById("tipos_discapacidad");
    const grado_discapacidad = document.getElementById("grado_discapacidad");
    const causa_discapacidad = document.getElementById("causa_discapacidad");

    const nacionalidad_busqueda = document.getElementById("nacionalidad_busqueda");
    const cedula_identidad_busqueda = document.getElementById("cedula_identidad_busqueda");

    const prefijos = ["0414", "0424", "0416", "0426", "0412", "0422"];
    
    const formulario_busqueda_usuario = document.getElementById("formulario_busqueda_usuario");

    const campos_discapacidad = document.getElementById("campos_discapacidad");

    function DominioSelect(select) {
        const dominios = [
            "@gmail.com",
            "@outlook.com",
            "@yahoo.com"
        ];

        dominios.forEach(dominio => {
            const option = document.createElement("option");
            option.value = dominio;
            option.textContent = dominio;
            select.appendChild(option);
        });
    }

    function ValidarCorreo(input) {
        input.addEventListener("keydown", function (e) {
            let caracter = e.key;

            let caracteres_denegado = [
                "@", "com", "net", "edu", "gov", "org", "ve", "es", "ar", "mx",
                " ", "(", ")", "[", "]", "{", "}", "<", ">", ",", ";", ":", "\\", "/",
                "'", "\"", "|", "°", "¬", "¿", "?", "¡", "!", "#", "$", "%", "^", "&",
                "*", "=", "+", "~", "`", "-", "´"
            ];

            if (caracteres_denegado.includes(caracter)) {
                e.preventDefault();
                return;
            }

            if (caracter === "." && input.value.includes(".")) {
                e.preventDefault();
                return;
            }

            if (caracter === "." && input.value.length === 0) {
                e.preventDefault();
                return;
            }
        });

        input.addEventListener("paste", function (e) {
            e.preventDefault();
        });
    }

    DominioSelect(dominio_principal);
    DominioSelect(dominio_secundaria);

    ValidarCorreo(correo_principal);
    ValidarCorreo(correo_secundaria);

    function llenar(select) {
        if (!select) return;

        prefijos.forEach(prefijo => {
            const option = document.createElement("option");
            option.value = prefijo;
            option.textContent = prefijo;
            select.appendChild(option);
        });
    }

    function validar(input) {
        if (!input) return;

        input.addEventListener("keydown", function (e) {

            const permitidas = ["Backspace", "ArrowLeft", "ArrowRight", "Delete", "Tab"];

            if (permitidas.includes(e.key)) return;

            if (!/^\d$/.test(e.key)) {
                e.preventDefault();
                return;
            }

            if (input.value.length >= 7) {
                e.preventDefault();
            }
        });

        input.addEventListener("paste", e => e.preventDefault());
    }    

    llenar(prefijo_telefono_principal);
    validar(num_telefono_principal);

    if (prefijo_telefono_principal && num_telefono_principal) {
        prefijo_telefono_principal.addEventListener("change", function () {
            num_telefono_principal.value = "";
            num_telefono_principal.disabled = false;
        });
    }

    llenar(prefijo_telefono_secundaria);
    validar(num_telefonico_secundaria);

    if (prefijo_telefono_secundaria && num_telefonico_secundaria) {
        prefijo_telefono_secundaria.addEventListener("change", function () {
            num_telefonico_secundaria.value = "";
            num_telefonico_secundaria.disabled = false;
        });
    }

    llenar(prefijo_telefono_representante);
    validar(numero_telefono_representante);

    if (prefijo_telefono_representante && num_telefonico_secundaria) {
        prefijo_telefono_representante.addEventListener("change", function () {
            numero_telefono_representante.value = "";
            numero_telefono_representante.disabled = false;
        });
    }
    
    llenar(prefijo_telefono_otrorepresentante);
    validar(numero_telefono_otrorepresentante);

    if (prefijo_telefono_otrorepresentante && num_telefonico_secundaria) {
        prefijo_telefono_otrorepresentante.addEventListener("change", function () {
            numero_telefono_otrorepresentante.value = "";
            numero_telefono_otrorepresentante.disabled = false;
        });
    }
    
    configurarCedula(nacionalidad, cedula_identidad)
    configurarCedula(nacionalidad_busqueda, cedula_identidad_busqueda)
    configurarCedula(nacionalidad_representante, cedula_identidad_representante)
    configurarCedula(nacionalidad_otrorepresentante, cedula_identidad_otrorepresentante)

    const parentescos = [
        "Madre",
        "Padre",
        "Tutor",
        "Abuelo/a",
        "Hermano/a"
    ];

    function llenarSelect(id) {
        const select = document.getElementById(id);

        select.innerHTML = `<option value="">Seleccione</option>`;

        parentescos.forEach(p => {
            const option = document.createElement("option");
            option.value = p;
            option.textContent = p;
            select.appendChild(option);
        });
    }

    llenarSelect("parestenco_representante");
    llenarSelect("otroparestenco");

    function configurarCedula(selectNacionalidad, inputCedula) {

        function longitud_identidad() {
            const nacionalidad = selectNacionalidad.value;

            if (nacionalidad === "") {
                inputCedula.value = "";
                inputCedula.disabled = true;
                inputCedula.placeholder = "Seleccione nacionalidad";
                return;
            }

            inputCedula.removeAttribute("minLength");
            inputCedula.removeAttribute("maxLength");

            switch (nacionalidad) {
                case "V":
                    inputCedula.disabled = false;
                    inputCedula.maxLength = 8;
                    inputCedula.minLength = 7;
                    inputCedula.placeholder = "Cédula de Identidad (7-8)";
                    break;

                case "E":
                    inputCedula.disabled = false;
                    inputCedula.maxLength = 10;
                    inputCedula.minLength = 8;
                    inputCedula.placeholder = "Pasaporte/DNI (8-10)";
                    break;
            }
        }

        inputCedula.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "");
        });

        selectNacionalidad.addEventListener("change", longitud_identidad);

        longitud_identidad();
    }

    function controlarFormularioPorPerfil(idPerfil) {
        document.querySelectorAll(".bloque-formulario")
            .forEach(el => el.style.display = "none");

        if (idPerfil == 5) {
            document.querySelector(".bloque-secundaria").style.display = "block";
            document.querySelector(".bloque-representante").style.display = "block";
            document.querySelector(".bloque-discapacidad").style.display = "block";
        } 
        else {
            document.querySelector(".bloque-profesion").style.display = "block";
        }
    }

    btn_otro_representante.addEventListener("click", () => {
        if (subcontenedor_representante.style.display === "none") {
            subcontenedor_representante.style.display = "block";
            btn_otro_representante.textContent = "Ocultar segundo representante";
        } else {
            subcontenedor_representante.style.display = "none";
            btn_otro_representante.textContent = "Agregar segundo representante";
        }
    });

    btn_discapacidad.addEventListener("click", () => {
        const visible = campos_discapacidad.style.display === "block";

        if (visible) {
            campos_discapacidad.style.display = "none";
            btn_discapacidad.textContent = "Mostrar";
        } else {
            campos_discapacidad.style.display = "block";
            btn_discapacidad.textContent = "Ocultar";
        }
    });

    formulario_busqueda_usuario.addEventListener("submit", async (e) => {        
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_busqueda_usuario)

            const respuesta = await fetch("/buscar_datos_usuario/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();

            if (resultado.estado === "fallo") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_busqueda_usuario.reset();

            controlarFormularioPorPerfil(resultado.perfil.id_perfil_id);

            perfil_usuario.value = resultado.perfil.id_perfil_id
            
            nombres_actualizar_usuario.value = resultado.usuario.nombres
            apellidos_actualizar_usuario.value = resultado.usuario.apellidos

            const option_genero = document.createElement("option")
            option_genero.value = resultado.usuario.genero
            option_genero.textContent = resultado.usuario.genero
            option_genero.selected = true
            option_genero.hidden = true
            genero_actualizar_usuario.append(option_genero)

            const [nacionalidad_usuario, cedula_usuario] = resultado.usuario.cedula_identidad.split("-");

            const option_nacionalidad = document.createElement("option")
            option_nacionalidad.value = nacionalidad_usuario
            option_nacionalidad.textContent = nacionalidad_usuario
            option_nacionalidad.selected = true
            option_nacionalidad.hidden = true
            nacionalidad.append(option_nacionalidad)

            cedula_identidad.value = cedula_usuario

            const option_estado_civil = document.createElement("option")
            option_estado_civil.value = resultado.usuario.estado_civil
            option_estado_civil.textContent = resultado.usuario.estado_civil
            option_estado_civil.selected = true
            option_estado_civil.hidden = true
            estado_civil_actualizar_usuario.append(option_estado_civil)
            
            let prefijo_principal = resultado.contacto.telefono_personal.slice(0, 4)
            let numero_principal = resultado.contacto.telefono_personal.slice(4, 11)

            const option_prefijo_principal = document.createElement("option")
            option_prefijo_principal.value = prefijo_principal
            option_prefijo_principal.textContent = prefijo_principal
            option_prefijo_principal.selected = true
            option_prefijo_principal.hidden = true
            prefijo_telefono_principal.append(option_prefijo_principal)

            num_telefono_principal.value = numero_principal

            let prefijo_secundario = resultado.contacto.telefono_suplete.slice(0, 4)
            let numero_secundario = resultado.contacto.telefono_suplete.slice(4, 11)

            const option_prefijo_secundaria = document.createElement("option")
            option_prefijo_secundaria.value = prefijo_secundario
            option_prefijo_secundaria.textContent = prefijo_secundario
            option_prefijo_secundaria.selected = true
            option_prefijo_secundaria.hidden = true
            prefijo_telefono_secundaria.append(option_prefijo_secundaria)

            num_telefonico_secundaria.value = numero_secundario
            
            const [nombre_correo_principal, dominio_principal_usuario] = resultado.contacto.correo_electronico.split("@");
 
            const option_dominio_principal = document.createElement("option")
            option_dominio_principal.value = "@" + dominio_principal_usuario
            option_dominio_principal.textContent = "@" + dominio_principal_usuario
            option_dominio_principal.selected = true
            option_dominio_principal.hidden = true
            dominio_principal.append(option_dominio_principal)

            correo_principal.value = nombre_correo_principal
            
            const [nombre_correo_secundario, dominio_secundario_usuario] = resultado.contacto.correo_alternativo.split("@");

            const option_dominio_secundario = document.createElement("option")
            option_dominio_secundario.value = "@" + dominio_secundario_usuario
            option_dominio_secundario.textContent = "@" + dominio_secundario_usuario
            option_dominio_secundario.selected = true
            option_dominio_secundario.hidden = true
            dominio_secundaria.append(option_dominio_secundario)

            correo_secundaria.value = nombre_correo_secundario

            const option_pais = document.createElement("option")
            option_pais.value = resultado.nacimiento.pais
            option_pais.textContent = resultado.nacimiento.pais
            option_pais.selected = true
            option_pais.hidden = true
            pais_nacimiento.append(option_pais)

            if (resultado.nacimiento.pais == "Venezuela") {
                const option_estado = document.createElement("option")
                option_estado.value = resultado.nacimiento.estado
                option_estado.textContent = resultado.nacimiento.estado
                option_estado.selected = true
                option_estado.hidden = true
                estado_nacimiento.append(option_estado)
            } else {
                estado_nacimiento.hidden = true

                estado_novzla.value = resultado.nacimiento.estado
                estado_novzla.hidden = false
            }

            if (resultado.nacimiento.pais == "Venezuela") {
                const option_municipio = document.createElement("option")
                option_municipio.value = resultado.nacimiento.municipio
                option_municipio.textContent = resultado.nacimiento.municipio
                option_municipio.selected = true
                option_municipio.hidden = true
                municipio_nacimiento.append(option_municipio)
            } else {
                municipio_nacimiento.hidden = true

                municipio_novzla.value = resultado.nacimiento.municipio
                municipio_novzla.hidden = false
            }

            if (resultado.nacimiento.pais == "Venezuela") {
                const option_parroquia = document.createElement("option")
                option_parroquia.value = resultado.nacimiento.parroquia
                option_parroquia.textContent = resultado.nacimiento.parroquia
                option_parroquia.selected = true
                option_parroquia.hidden = true
                parroquia_nacimiento.append(option_parroquia)
            } else {
                parroquia_nacimiento.hidden = true

                parroquia_novzla.value = resultado.nacimiento.parroquia
                parroquia_novzla.hidden = false
            }

            direccion_nacimiento.value = resultado.nacimiento.direccion_nacimiento
            
            fecha_nacimiento.value = resultado.nacimiento.fecha_nacimiento

            const option_condicion_residencia = document.createElement("option")
            option_condicion_residencia.value = resultado.residencia.condicion_residencia
            option_condicion_residencia.textContent = resultado.residencia.condicion_residencia
            option_condicion_residencia.selected = true
            option_condicion_residencia.hidden = true
            condicion_residencia.append(option_condicion_residencia)

            const option_municipio_residencia = document.createElement("option")
            option_municipio_residencia.value = resultado.residencia.municipio
            option_municipio_residencia.textContent = resultado.residencia.municipio
            option_municipio_residencia.selected = true
            option_municipio_residencia.hidden = true
            municipio_residencia.append(option_municipio_residencia)
            
            const option_parroquia_residencia = document.createElement("option")
            option_parroquia_residencia.value = resultado.residencia.parroquia
            option_parroquia_residencia.textContent = resultado.residencia.parroquia
            option_parroquia_residencia.selected = true
            option_parroquia_residencia.hidden = true
            parroquia_residencia.append(option_parroquia_residencia)

            direccion_domicilio.value = resultado.residencia.direccion_residencia

            if (resultado.profesion) {
                profesion_usuario.value = resultado.profesion.profesion_pregrado
                universidad_usuario.value = resultado.profesion.universidad_egreso_pregrado

                const option_pais_profesion = document.createElement("option")
                option_pais_profesion.value = resultado.profesion.pais_profesion_pregrado
                option_pais_profesion.textContent = resultado.profesion.pais_profesion_pregrado
                option_pais_profesion.selected = true
                option_pais_profesion.hidden = true
                pais_profesion.append(option_pais_profesion)
            }

            if (resultado.informacion_secundaria) {
                const option_tipo_institucion = document.createElement("option")
                option_tipo_institucion.value = resultado.informacion_secundaria.tipo_institucion
                option_tipo_institucion.textContent = resultado.informacion_secundaria.tipo_institucion
                option_tipo_institucion.selected = true
                option_tipo_institucion.hidden = true
                tipos_secundaria.append(option_tipo_institucion)

                nombre_liceo.value = resultado.informacion_secundaria.nombre_institucion
                fecha_grado.value = resultado.informacion_secundaria.fecha_grado
                codigo_sin_opsu.value = resultado.informacion_secundaria.codigo_sni_opsu
            }

            if (resultado.representantes && resultado.representantes.length > 0) {

                const rep1 = resultado.representantes[0];

                nombres_representante.value = rep1.nombres;
                apellidos_representante.value = rep1.apellidos;

                const [nac1, ced1] = rep1.cedula_identidad.split("-");
                nacionalidad_representante.value = nac1;
                cedula_identidad_representante.value = ced1;

                let tel1 = rep1.telefono;
                prefijo_telefono_representante.value = tel1.slice(0, 4);
                numero_telefono_representante.value = tel1.slice(4);

                parestenco_representante.value = rep1.parentesco;

                if (resultado.representantes.length > 1) {

                    const rep2 = resultado.representantes[1];

                    nombres_otrorepresentante.value = rep2.nombres;
                    apellidos_otrorepresentante.value = rep2.apellidos;

                    const [nac2, ced2] = rep2.cedula_identidad.split("-");
                    nacionalidad_otrorepresentante.value = nac2;
                    cedula_identidad_otrorepresentante.value = ced2;

                    let tel2 = rep2.telefono;
                    prefijo_telefono_otrorepresentante.value = tel2.slice(0, 4);
                    numero_telefono_otrorepresentante.value = tel2.slice(4);

                    otroparestenco.value = rep2.parentesco;
                }
            }

            if (resultado.discapacidad) {
                codigo_carnet_dispacidad.value = resultado.discapacidad.codigo_carnet_discapacidad

                codigo_carnet_dispacidad.value = resultado.discapacidad.nro_registro_medico

                const option_tipo_discapacidad = document.createElement("option")
                option_tipo_discapacidad.value = resultado.discapacidad.tipo_discapacidad
                option_tipo_discapacidad.textContent = resultado.discapacidad.tipo_discapacidad
                option_tipo_discapacidad.selected = true
                option_tipo_discapacidad.hidden = true
                tipos_discapacidad.append(option_tipo_discapacidad)

                const option_grado_discapacidad = document.createElement("option")
                option_grado_discapacidad.value = resultado.discapacidad.grado_discapacidad
                option_grado_discapacidad.textContent = resultado.discapacidad.grado_discapacidad
                option_grado_discapacidad.selected = true
                option_grado_discapacidad.hidden = true
                grado_discapacidad.append(option_grado_discapacidad)

                const option_causa_discapacidad = document.createElement("option")
                option_causa_discapacidad.value = resultado.discapacidad.causa_discapacidad
                option_causa_discapacidad.textContent = resultado.discapacidad.causa_discapacidad
                option_causa_discapacidad.selected = true
                option_causa_discapacidad.hidden = true
                causa_discapacidad.append(option_causa_discapacidad)
            }            
        } catch (error) {
            console.error(error)
        }
    });

    formulario_actualizar_usuario.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_actualizar_usuario);

            const respuesta = await fetch("/modulo_actualizar_usuarios/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();

            if (resultado.estado == "ok") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
            formulario_actualizar_usuario.reset();
        } catch (error) {
            console.error(error);
        }
    });
});