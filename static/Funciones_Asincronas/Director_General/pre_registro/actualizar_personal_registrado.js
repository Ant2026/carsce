document.addEventListener("DOMContentLoaded", () => {

    const formulario_busqueda = document.getElementById("formulario_busqueda");
    const select_nacionalidad = document.getElementById("nacionalidad");
    const input_cedula_identidad = document.getElementById("cedula_identidad");

    const formulario_actualizar = document.getElementById("formulario_actualizar");
    const input_nombres_usuario = document.getElementById("nombres_usuario");
    const input_apellidos_usuario = document.getElementById("apellidos_usuario");
    const input_cedula_usuario = document.getElementById("cedula_usuario");

    const contenedor_perfiles_asignado = document.getElementById("contenedor_perfiles_asignado");
    const contenedor_asignar_perfiles = document.getElementById("contenedor_asignar_perfiles");

    configurarCedula(select_nacionalidad, input_cedula_identidad);

    formulario_busqueda.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_busqueda);

            const respuesta = await fetch("/bus_per_asig/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado == "fallo") {
                await Swal.fire({
                    title: resultado.title,
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
                return;
            }

            input_nombres_usuario.value = resultado.usuario.nombres;
            input_apellidos_usuario.value = resultado.usuario.apellidos;
            input_cedula_usuario.value = resultado.usuario.cedula;

            mostrar_perfiles_asignados(resultado.perfiles);

            mostrar_perfiles_disponibles(
                resultado.perfiles_disponibles,
                resultado.pnfs_disponibles_docente,
                resultado.pnfs_disponibles_coordinador
            );
        } catch (error) {
            console.error(error);
        }
    });

    function mostrar_perfiles_asignados(perfiles) {
        // Limpiar el contenedor antes de cargar nuevos datos
        contenedor_perfiles_asignado.innerHTML = "";

        if (!perfiles || perfiles.length === 0) {
            contenedor_perfiles_asignado.innerHTML = `
                <div class="mensaje_sin_perfiles">
                    <p>El usuario no tiene perfiles asignados.</p>
                </div>
            `;
            return;
        }

        perfiles.forEach((perfil, index) => {
            const contenedor = document.createElement("div");

            contenedor.classList.add("perfil_asignado");

            contenedor.innerHTML = `
                <div class="campo_perfil">
                    <label>Perfil</label>
                    <input type="text" value="${perfil.rol}" readonly>
                </div>

                <div class="campo_perfil">
                    <label>P.N.F</label>
                    <input type="text" value="${perfil.pnf}" readonly>
                </div>

                <div class="campo_perfil">
                    <label>Núcleo</label>
                    <input type="text" value="${perfil.nucleo}" readonly>
                </div>

                <div class="campo_perfil">
                    <label>Estado</label>
                    <input type="text" value="${perfil.estado}" readonly>
                </div>
            `;

            contenedor_perfiles_asignado.appendChild(contenedor);
        });
    }

    function mostrar_perfiles_disponibles(perfiles, pnfs_docente, pnfs_coordinador) {
        contenedor_asignar_perfiles.innerHTML = "";

        if (!perfiles || perfiles.length === 0) {
            contenedor_asignar_perfiles.innerHTML = `
                <div class="mensaje_sin_perfiles">
                    <p>El usuario ya tiene todos los perfiles asignados.</p>
                </div>
            `;
            return;
        }

        perfiles.forEach(perfil => {
            const contenedor = document.createElement("div");

            contenedor.classList.add("perfil_disponible");

            // DOCENTE
            if (perfil.tipo === "docente") {
                let opciones_pnf = "";
                if (pnfs_docente && pnfs_docente.length > 0) {
                    pnfs_docente.forEach(pnf => {

                        opciones_pnf += `
                            <label class="checkbox_pnf">
                                <input type="checkbox" name="pnfs_docente" value="${pnf.id_pnf}" data-pnf="${pnf.pnf}">
                                <span>${pnf.pnf} (${pnf.codigo})</span>
                            </label>
                        `;
                    });
                } else {
                    opciones_pnf = `
                        <p class="mensaje_sin_pnf">
                            No existen P.N.F disponibles para asignar.
                        </p>
                    `;
                }


                contenedor.innerHTML = `
                    <div class="campo_perfil">
                        <label>Perfil disponible</label>
                        <input type="text" value="${perfil.rol}" readonly>
                    </div>
                    <div class="contenedor_pnfs_disponibles">
                        <label class="titulo_pnf">Seleccionar P.N.F</label>
                        <div class="lista_checkbox_pnf">${opciones_pnf}</div>
                    </div>
                `;
            }

            // COORDINADOR PNF
            else if (perfil.tipo === "coordinador_pnf") {
                let opciones_pnf = "";

                if (pnfs_coordinador && pnfs_coordinador.length > 0) {
                    pnfs_coordinador.forEach(pnf => {

                        opciones_pnf += `
                            <label class="checkbox_pnf">
                                <input type="checkbox" name="pnfs_coordinador" value="${pnf.id_pnf}" data-pnf="${pnf.pnf}">
                                <span>${pnf.pnf} (${pnf.codigo})</span>
                            </label>
                        `;

                    });

                } else {

                    opciones_pnf = `
                        <p class="mensaje_sin_pnf">
                            No existen P.N.F disponibles para asignar.
                        </p>
                    `;
                }


                contenedor.innerHTML = `
                    <div class="campo_perfil">
                        <label>Perfil disponible</label>
                        <input type="text" value="${perfil.rol}" readonly>
                    </div>
                    <div class="contenedor_pnfs_disponibles">
                        <label class="titulo_pnf">Seleccionar P.N.F</label>
                        <div class="lista_checkbox_pnf">${opciones_pnf}</div>
                    </div>
                `;

            } else { // CONTROL DE ESTUDIO
                contenedor.innerHTML = `
                    <div class="campo_perfil">
                        <label>Perfil disponible</label>
                        <input type="text" value="${perfil.rol}" readonly>
                    </div>
                `;
            }

            contenedor_asignar_perfiles.appendChild(contenedor);
        });
    }

    formulario_actualizar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizar);

            const respuesta = await fetch("/act_per_asig/", {
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
                formulario_actualizar.reset();
            }
        } catch (error) {
            console.error(error);
        }
    });
});