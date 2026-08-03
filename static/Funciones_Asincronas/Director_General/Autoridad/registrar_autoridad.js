document.addEventListener("DOMContentLoaded", () => {

    const formulario_registrar = document.getElementById("formulario_registrar_autoridades");
   
    const input_cedula_identidad = document.getElementById("cedula_identidad");
    const select_nacionalidad = document.getElementById("nacionalidad");
    const msj_cedula_identidad = document.getElementById("mensaje_cedula_identidad");

    const select_cargo_autoridades = document.getElementById("cargo_autoridades");

    const resolucion_autoridades = document.getElementById("resolucion_autoridades");
    const msg_resolucion = document.getElementById("msg_resolucion");

    const btn_registrar = document.getElementById("btn_registrar");

    configurarCedula(select_nacionalidad, input_cedula_identidad);

    resolucion_autoridades.addEventListener("input", function () {
        let valor = this.value.toUpperCase().replace(/[^A-Z0-9]/g, "");

        let letras = valor.replace(/[^A-Z]/g, "").slice(0, 6);
        let numeros = valor.replace(/[^0-9]/g, "").slice(0, 6);

        this.value = letras + numeros;
    });
    
    async function cargo_autoridades() {
        try {
            const respuesta = await fetch("/cargo_asig_aut/");
            const resultado = await respuesta.json();
            console.log(resultado);

            select_cargo_autoridades.innerHTML = "<option value='' selected>Selecciona una opción</option>";

            if (resultado.cargo.length > 0) {
                resultado.cargo.forEach(cargo => {
                    const option = document.createElement("option");
                    option.value = cargo;
                    option.textContent = cargo;
                    select_cargo_autoridades.append(option);
                });

                btn_registrar.disabled = false;
            } else {
                btn_registrar.disabled = true;
            }
        } catch (error) {
            console.error(error);
        }
    }
    cargo_autoridades();

    async function validarCedula(selectNacionalidad, inputCedula, mensaje) {
        const nacionalidad = selectNacionalidad.value;
        const cedula = inputCedula.value.trim();

        if (cedula.length === 0) {
            mensaje.textContent = "";
            inputCedula.setCustomValidity("");
            inputCedula.classList.remove("is-valid", "is-invalid");
            btn_registrar.disabled = false;
            return;
        }

        try {
            const formulario = new FormData();
            formulario.append("nacionalidad", nacionalidad);
            formulario.append("cedula", cedula);

            const respuesta = await fetch("/val_ci_aut/", {
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
                    "Ya se encuentra una autoridad registrado con esta cédula de identidad."
                );

                inputCedula.classList.add("is-invalid");
                inputCedula.classList.remove("is-valid");

                mensaje.textContent = "Ya se encuentra un autoridad registrado con esta cédula de identidad.";
                mensaje.style.color = "#dc3545";

                btn_registrar.disabled = true;
            } else {
                inputCedula.setCustomValidity("");

                inputCedula.classList.remove("is-invalid");
                inputCedula.classList.add("is-valid");

                mensaje.textContent = "La cédula de identidad está disponible.";
                mensaje.style.color = "#198754";

                btn_registrar.disabled = false;
            }

        } catch (error) {
            console.error(error);
        }
    }

    select_nacionalidad.addEventListener("change", async () => {
        validarCedula(select_nacionalidad, input_cedula_identidad, msj_cedula_identidad);
    });

    input_cedula_identidad.addEventListener("input", async () => {
        validarCedula(select_nacionalidad, input_cedula_identidad, msj_cedula_identidad);
    });

    async function validarResolucion(inputresolucion, mensaje) {
        const resolucion = inputresolucion.value.trim();

        if (resolucion.length === 0) {
            mensaje.textContent = "";
            inputresolucion.setCustomValidity("");
            inputresolucion.classList.remove("is-valid", "is-invalid");
            btn_registrar.disabled = false;
            return;
        }

        try {
            const formulario = new FormData();
            formulario.append("resolucion", resolucion);

            const respuesta = await fetch("/val_resolucion/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.existe) {
                inputresolucion.setCustomValidity("Ya existe una autoridad registrada con esta resolución.");
                inputresolucion.classList.add("is-invalid");
                inputresolucion.classList.remove("is-valid");

                mensaje.textContent = "Ya existe una autoridad registrada con esta resolución.";
                mensaje.style.color = "#dc3545";

                btn_registrar.disabled = true;

            } else {
                inputresolucion.setCustomValidity("");
                inputresolucion.classList.remove("is-invalid");
                inputresolucion.classList.add("is-valid");

                mensaje.textContent = "La resolución está disponible.";
                mensaje.style.color = "#198754";

                btn_registrar.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    resolucion_autoridades.addEventListener("input", async () => {
        await validarResolucion(resolucion_autoridades, msg_resolucion);
    });

    resolucion_autoridades.addEventListener("paste", async () => {
        await validarResolucion(resolucion_autoridades, msg_resolucion);
    });

    formulario_registrar.addEventListener("submit", async function (e) {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar)

            const respuesta = await fetch("/reg_auts/", {
                method: "POST",
                body: formulario
            });
             const resultado = await respuesta.json()
            console.log(resultado)

            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_registrar.reset();
            }
        } catch (error) {
            console.error(error)
        }
    });

}); 