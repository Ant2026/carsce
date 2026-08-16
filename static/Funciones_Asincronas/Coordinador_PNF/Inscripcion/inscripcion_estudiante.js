document.addEventListener("DOMContentLoaded", () => {
    const contenedor_pre_inscripcion = document.getElementById("contenedor_pre_inscripcion")

    const dialogo = document.getElementById("datos_estudiantes")
    const btn_cerrar_dialogo = document.getElementById("cerrar_dialogo")

    const control_nombre_estudiante = document.getElementById("nombres_estudiante")
    const control_apellido_estudiante = document.getElementById("apellidos_estudiante")
    const control_ci_estudiante = document.getElementById("ci_estudiante")
    const control_genero_estudiante = document.getElementById("genero_estudiante")
    const control_estado_civil_estudiante = document.getElementById("estado_civil_estudiante")

    const control_telefono_principal = document.getElementById("telefono_principal")
    const control_telefono_secundario = document.getElementById("telefono_secundario")
    const control_correo_principal = document.getElementById("correo_principal")
    const control_correo_secundario = document.getElementById("correo_secundario")

    const control_nombres_representante = document.getElementById("nombres_representante")
    const control_apellidos_representante = document.getElementById("apellidos_representante")
    const control_ci_representante = document.getElementById("ci_representante")
    const control_telefono_representante = document.getElementById("telefono_representante")
    const control_parentesco_representante = document.getElementById("parentesco_representante")

    const control_pais_nacimiento = document.getElementById("pais_nacimiento")
    const control_estado_nacimiento = document.getElementById("estado_nacimiento")
    const control_municipio_nacimiento = document.getElementById("municipio_nacimiento")
    const control_parroquia_nacimiento = document.getElementById("parroquia_nacimiento")
    const control_direccion_nacimiento = document.getElementById("direccion_nacimiento")
    const control_fecha_nacimiento = document.getElementById("fecha_nacimiento")

    const control_condicion_residencia = document.getElementById("condicion_residencia")
    const control_municipio_residencia = document.getElementById("municipio_residencia")
    const control_parroquia_residencia = document.getElementById("parroquia_residencia")
    const control_direccion_residencia = document.getElementById("direccion_residencia")

    const control_codigo_carnet = document.getElementById("codigo_carnet")
    const control_nro_registro = document.getElementById("nro_registro")
    const control_tipos_discapacidad = document.getElementById("tipos_discapacidad")
    const control_grados_discapacidad = document.getElementById("grados_discapacidad")
    const control_causa_discapacidad = document.getElementById("causa_discapacidad")

    const control_img_ci = document.getElementById("contenedor_ci_estudiante")
    const control_img_bachiller = document.getElementById("contenedor_titulo_bachiller_estudiante")
    const control_img_sabana = document.getElementById("contenedor_sabana_nota_estudiante")
    const control_img_opsu = document.getElementById("contenedor_opsu_estudiante")

    let pnf = "", nucleo = ""

    function getCookie(nombre) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(nombre + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(nombre.length + 1)
                    );
                    break;
                }
            }
        }

        return cookieValue;
    }
    const csrftoken = getCookie("csrftoken");

    async function estudiante_pre_inscripcion() {
        try {
            const respuesta = await fetch("/obt_pre_inscrt/");
            const resultado = await respuesta.json();
            console.log(resultado);

            contenedor_pre_inscripcion.innerHTML = "";

            let opciones = "";
            if (resultado.secciones.length > 0) {
                opciones += `
                    <option value="" selected>
                        Seleccione una sección
                    </option>`;

                resultado.secciones.forEach(seccion => {
                    opciones += `
                        <option value="${seccion.id_seccion}">
                            ${seccion.nombre} | ${seccion.turno}
                        </option>
                    `;
                });
            } else {
                opciones = ` <option value=""> No hay secciones disponibles</option>`;
            }

            resultado.estudiantes.forEach((estudiante, index) => {
                contenedor_pre_inscripcion.innerHTML += `
                    <tr data-cedula="${estudiante.cedula_identidad}">
                        <td>${index + 1}</td>
                        <td>${estudiante.nombres}</td>
                        <td>${estudiante.apellidos}</td>
                        <td>${estudiante.cedula_identidad}</td>

                        <td>
                            <select name="seccion" class="select_seccion">
                                ${opciones}
                            </select>
                        </td>
                        <td>
                            <button type="button" class="inscribir">
                                Inscribir
                            </button>
                        </td>
                        <td>
                            <button type="button" class="rechazar">
                                Rechazar
                            </button>
                        </td>
                    </tr>
                `;
            });
        } catch (error) {
            console.error(error);
        }
    }
    estudiante_pre_inscripcion();

    document.addEventListener("change", async function (e) {
        if (!e.target.classList.contains("select_seccion")) return;
        const select = e.target;
        const opcionSeleccionada = select.options[select.selectedIndex];

        const cantidad = parseInt(opcionSeleccionada.dataset.cantidad || 0);
        if (cantidad >= 48) {
            const resultado = await Swal.fire({
                title: "Sección llena",
                text: `La sección ya posee ${cantidad} estudiantes. ¿Desea continuar con la inscripción?`,
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Sí, continuar",
                cancelButtonText: "Cancelar",
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (!resultado.isConfirmed) {
                select.value = "";
            }
        }
    });

    contenedor_pre_inscripcion.addEventListener("click", async (e) => {
        const fila = e.target.closest("tr");
        if (e.target.closest("select") ||
            e.target.closest("button") ||
            e.target.closest("form")) {
            return;
        }
        dialogo.showModal()

        const formulario = new FormData();
        formulario.append("cedula_estudiante", fila.dataset.cedula);

        const respuesta = await fetch("/obt_data_est/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            },
            body: formulario
        });
        const resultado = await respuesta.json();
        console.log(resultado);

        control_nombre_estudiante.value = resultado.usuario.nombres
        control_apellido_estudiante.value = resultado.usuario.apellidos
        control_ci_estudiante.value = resultado.usuario.cedula_identidad
        control_genero_estudiante.value = resultado.usuario.genero
        control_estado_civil_estudiante.value = resultado.usuario.estado_civil

        control_telefono_principal.value = resultado.contacto.telefono_suplete
        control_telefono_secundario.value = resultado.contacto.telefono_personal
        control_correo_principal.value = resultado.contacto.correo_electronico
        control_correo_secundario.value = resultado.contacto.correo_alternativo

        if (resultado.representantes.length > 0) {
            const representante = resultado.representantes[0];
            control_nombres_representante.value = representante.nombres;
            control_apellidos_representante.value = representante.apellidos;
            control_ci_representante.value = representante.cedula_identidad;
            control_telefono_representante.value = representante.telefono;
            control_parentesco_representante.value = representante.parentesco;
        }

        control_pais_nacimiento.value = resultado.nacimiento.pais
        control_estado_nacimiento.value = resultado.nacimiento.estado
        control_municipio_nacimiento.value = resultado.nacimiento.municipio
        control_parroquia_nacimiento.value = resultado.nacimiento.parroquia
        control_direccion_nacimiento.value = resultado.nacimiento.direccion_nacimiento
        control_fecha_nacimiento.value = resultado.nacimiento.fecha_nacimiento

        control_condicion_residencia.value = resultado.residencia.condicion_residencia
        control_municipio_residencia.value = resultado.residencia.municipio
        control_parroquia_residencia.value = resultado.residencia.parroquia
        control_direccion_residencia.value = resultado.residencia.direccion_residencia

        control_codigo_carnet.value = resultado.discapacidad.codigo_carnet_discapacidad
        control_nro_registro.value = resultado.discapacidad.nro_registro_medico
        control_tipos_discapacidad.value = resultado.discapacidad.tipo_discapacidad
        control_grados_discapacidad.value = resultado.discapacidad.grado_discapacidad
        control_causa_discapacidad.value = resultado.discapacidad.causa_discapacidad

        control_img_ci.innerHTML = "";
        control_img_bachiller.innerHTML = "";
        control_img_sabana.innerHTML = "";
        control_img_opsu.innerHTML = "";

        if (Array.isArray(resultado.documentos)) {
            resultado.documentos.forEach(documento => {
                const url = documento.archivo.toLowerCase();
                let elemento;

                if (url.endsWith(".pdf")) {
                    elemento = document.createElement("embed");
                    elemento.src = documento.archivo;
                    elemento.type = "application/pdf";
                    elemento.width = "100%";
                    elemento.height = "400px";
                } else if (
                    url.endsWith(".jpg") || url.endsWith(".jpeg") || url.endsWith(".png") || url.endsWith(".webp")) {
                    elemento = document.createElement("img");
                    elemento.src = documento.archivo;
                    elemento.style.maxWidth = "250px";
                    elemento.style.height = "auto";
                } else {
                    console.warn("Formato no soportado:", documento.archivo);
                    return;
                }

                if (documento.tipo_documento === "Cédula de Identidad") {
                    control_img_ci.appendChild(elemento);
                }
                else if (documento.tipo_documento === "Título de Bachiller") {
                    control_img_bachiller.appendChild(elemento);
                }
                else if (documento.tipo_documento === "Sabana de Notas") {
                    control_img_sabana.appendChild(elemento);
                }
                else if (documento.tipo_documento === "OPSU") {
                    control_img_opsu.appendChild(elemento);
                }
            });
        }
    });

    btn_cerrar_dialogo.addEventListener("click", () => {
        dialogo.close()
    });

    const paginas = [
        document.getElementById("contenedor_datos_basicos"),
        document.getElementById("contacto_estudiante"),
        document.getElementById("contenedor_representante"),
        document.getElementById("contenedor_nacimiento"),
        document.getElementById("contenedor_residencia"),
        document.getElementById("contenedor_discapacidad"),
        document.getElementById("contenedor_ci_estudiante"),
        document.getElementById("contenedor_titulo_bachiller_estudiante"),
        document.getElementById("contenedor_sabana_nota_estudiante"),
        document.getElementById("contenedor_opsu_estudiante")
    ];

    const btnAvanzar = document.getElementById("avanzar");
    const btnRetroceder = document.getElementById("retroceder");

    let paginaActual = 0;

    function mostrarPagina() {
        paginas.forEach((pagina, indice) => {
            pagina.style.display = indice === paginaActual ? "block" : "none";
        });

        btnRetroceder.disabled = paginaActual === 0;
        btnAvanzar.disabled = paginaActual === paginas.length - 1;

        window.scrollTo({ top: 0, behavior: "smooth" });
    }
    mostrarPagina();

    btnAvanzar.addEventListener("click", () => {
        if (paginaActual < paginas.length - 1) {
            paginaActual++;
            mostrarPagina();
        }
    });

    btnRetroceder.addEventListener("click", () => {
        if (paginaActual > 0) {
            paginaActual--;
            mostrarPagina();
        }
    });

    contenedor_pre_inscripcion.addEventListener("click", async (e) => {
        if (!e.target.classList.contains("inscribir") && !e.target.classList.contains("rechazar")) {
            return;
        }

        const fila = e.target.closest("tr");
        const cedula = fila.dataset.cedula;
        const seccion = fila.querySelector(".select_seccion").value;
        const accion = e.target.classList.contains("inscribir") ? "aceptado" : "rechazado";

        try {
            const formulario = new FormData();
            formulario.append("cedula", cedula);
            formulario.append("seccion", seccion);
            formulario.append("accion", accion);

            const respuesta = await fetch("/inscr_est/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                title: resultado.titulo,
                text: resultado.descripcion,
                icon: resultado.icon
            });
        } catch (error) {
            console.error(error);
        }
    });
});