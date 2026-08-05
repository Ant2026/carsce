document.addEventListener("DOMContentLoaded", () => {
    const select_registrar_pnfs = document.getElementById("pnfs_registrar_materia");
    
    const nombres_registrar_materias = document.getElementById("nombres_registrar_materias");
    const mensaje_nombre_materia = document.getElementById("mensaje_nombre_materia");
    
    const codigos_registrar_materias = document.getElementById("codigos_registrar_materias");
    const mensaje_codigo_materia = document.getElementById("mensaje_codigo_materia");

    const btn_registro = document.getElementById("btn_registrar");

    const select_periodo_academico = document.getElementById("periodo_registrar_materia");
    const select_trayecto_academico = document.getElementById("trayecto_registrar_materia");
    const select_pnfs_academico = document.getElementById("pnfs_registrar_materia");

    const formulario_registrar = document.getElementById("formulario_registrar");

    document.querySelectorAll("#THEA, #THEI").forEach(input => {
        input.addEventListener("input", function () {
            let valor = this.value.replace(/[^0-9,]/g, "");

            // Permitir una sola coma
            const partes = valor.split(",");
            if (partes.length > 2) {
                valor = partes[0] + "," + partes.slice(1).join("");
            }

            if (valor.includes(",")) {
                let [entero, decimal] = valor.split(",");
                valor = entero.slice(0, 2) + "," + decimal.slice(0, 1);
            } else {
                valor = valor.slice(0, 2);
            }

            this.value = valor;
        });
    });

    select_periodo_academico.addEventListener("change", function () {
        select_trayecto_academico.innerHTML = "";

        let opciones = [];

        const valor = this.value;

        if(valor){
            pnfs_registrados(valor);
        }

        if (
            valor === "INICIAL_TRIMESTRE" || 
            valor === "INICIAL_SEMESTRE"
        ) {
            opciones = ["Inicial"];
        } else if (
            valor === "TRIMESTRE" ||
            valor === "TRAMO_I" ||
            valor === "TRAMO_II" ||
            valor === "TRAMO_III" ||
            valor === "TRAMO_I_II" ||
            valor === "TRAMO_II_III" ||
            valor === "TRAMO_I_III"
        ) {
            opciones = [
                "Trayecto I",
                "Trayecto II",
                "Trayecto III",
                "Trayecto IV"
            ];
        } else if (
            valor === "SEMESTRE" ||
            valor === "SEMESTRE_I" ||
            valor === "SEMESTRE_II"
        ) {
            opciones = [
                "Trayecto I",
                "Trayecto II",
                "Trayecto III",
                "Trayecto IV",
                "Trayecto V"
            ]
        }

        if (opciones.length > 0) {
            select_trayecto_academico.disabled = false;
            select_trayecto_academico.innerHTML = `<option value="">Seleccionar Trayecto</option>`;

            opciones.forEach(item => {
                const option = document.createElement("option");
                option.value = item;
                option.textContent = item;
                select_trayecto_academico.appendChild(option);
            });
        } else {
            select_trayecto_academico.disabled = true;
            select_trayecto_academico.innerHTML = `<option value="">No disponible</option>`;
        }
    });

    async function pnfs_registrados(periodo_academico) {
        try {
            const formulario = new FormData();
            formulario.append("periodo_academico", periodo_academico);

            const respuesta = await fetch("/pnf_per_acad/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            select_registrar_pnfs.innerHTML = "<option value='' selected>Seleccionar el P.N.F</option>";

            resultado.nucleos.forEach(nucleo => {
                nucleo.pnfs.forEach(pnf => {
                    const option = document.createElement("option");
                    option.value = pnf.id_pnf;
                    option.textContent = pnf.pnf;
                    select_registrar_pnfs.appendChild(option);
                });
            });
        } catch (error) {
            console.error(error)
        }
    }

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/reg_mat/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_registrar.reset()
            } 
        } catch (error) {
            console.error(error)
        }
    });

    async function validar_nombre_materia() {
        try {
            const formulario = new FormData();
            formulario.append("nombre", nombres_registrar_materias.value);

            const respuesta = await fetch("/nombre_materia/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });

            const resultado = await respuesta.json();

            if (resultado.existe) {
                nombres_registrar_materias.setCustomValidity("Ya existe una materia con ese nombre.");
                nombres_registrar_materias.classList.add("is-invalid");
                nombres_registrar_materias.classList.remove("is-valid");

                mensaje_nombre_materia.textContent = "Ya existe una materia con ese nombre.";
                mensaje_nombre_materia.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                nombres_registrar_materias.setCustomValidity("");
                nombres_registrar_materias.classList.add("is-valid");
                nombres_registrar_materias.classList.remove("is-invalid");

                mensaje_nombre_materia.textContent = "El nombre de la materia está disponible.";
                mensaje_nombre_materia.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    nombres_registrar_materias.addEventListener("input", validar_nombre_materia);

    async function validar_codigo_materia() {
        try {
            const formulario = new FormData();
            formulario.append("codigo", codigos_registrar_materias.value);

            const respuesta = await fetch("/codigo_materia/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();

            if (resultado.existe) {
                codigos_registrar_materias.setCustomValidity("Ya existe una materia con ese código.");
                codigos_registrar_materias.classList.add("is-invalid");
                codigos_registrar_materias.classList.remove("is-valid");

                mensaje_codigo_materia.textContent = "Ya existe una materia con ese código.";
                mensaje_codigo_materia.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                codigos_registrar_materias.setCustomValidity("");
                codigos_registrar_materias.classList.add("is-valid");
                codigos_registrar_materias.classList.remove("is-invalid");

                mensaje_codigo_materia.textContent = "El código de la materia está disponible.";
                mensaje_codigo_materia.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    codigos_registrar_materias.addEventListener("input", validar_codigo_materia);

    codigos_registrar_materias.addEventListener("input", function () {
        this.value = this.value
            .toUpperCase()
            .replace(/[^A-Z0-9]/g, "")
            .slice(0, 7); 
    });
});