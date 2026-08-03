document.addEventListener("DOMContentLoaded", () => {
    const formulario_registrar = document.getElementById("formulario_registrar");
    const contenedor_registrar_nucleos = document.getElementById("contenedor_registrar_nucleos");

    const input_nombre_pnf = document.getElementById("registrar_nombre_pnf");
    const mensaje_nombre_pnf = document.getElementById("mensaje_nombre_pnf");

    const input_codigo_pnf = document.getElementById("registrar_codigo_pnf");
    const mensaje_codigo_pnf = document.getElementById("mensaje_codigo_pnf");

    const btn_registro = document.getElementById("btn_registro");

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/reg_pnf/", {
                method: "POST",
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
                formulario_registrar.reset();
            }
        } catch (error) {
            console.error(error);
        }
    });

    async function validar_nombre_pnf() {
        try {
            const formulario = new FormData();
            formulario.append("nombrepnf", input_nombre_pnf.value);

            const respuesta = await fetch("/nombre_pnf/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            if (resultado.existe) {
                input_nombre_pnf.setCustomValidity("Ya existe un pnf con el mismo nombre.");
                input_nombre_pnf.classList.add("is-invalid");
                input_nombre_pnf.classList.remove("is-valid");

                mensaje_nombre_pnf.textContent = "Ya existe un pnf con el mismo nombre.";
                mensaje_nombre_pnf.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                input_nombre_pnf.setCustomValidity("");
                input_nombre_pnf.classList.add("is-valid");
                input_nombre_pnf.classList.remove("is-invalid");

                mensaje_nombre_pnf.textContent = "El nombre del PNF está disponible.";
                mensaje_nombre_pnf.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_nombre_pnf.addEventListener("input", async () => {
        await validar_nombre_pnf();
    });

    async function validar_codigo_pnf() {
        try {
            const formulario = new FormData();
            formulario.append("codigopnf", input_codigo_pnf.value);

            const respuesta = await fetch("/codigo_pnf/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.existe) {
                input_codigo_pnf.setCustomValidity("Ya existe un pnf con el mismo código.");
                input_codigo_pnf.classList.add("is-invalid");
                input_codigo_pnf.classList.remove("is-valid");

                mensaje_codigo_pnf.textContent = "Ya existe un pnf con el mismo código.";
                mensaje_codigo_pnf.style.color = "#dc3545";

                btn_registro.disabled = true;
            } else {
                input_codigo_pnf.setCustomValidity("");
                input_codigo_pnf.classList.add("is-valid");
                input_codigo_pnf.classList.remove("is-invalid");

                mensaje_codigo_pnf.textContent = "El código del PNF está disponible.";
                mensaje_codigo_pnf.style.color = "#198754";

                btn_registro.disabled = false;
            }
        } catch (error) {
            console.error(error);
        }
    }

    input_codigo_pnf.addEventListener("input", async () => {
        if (input_codigo_pnf.value.trim() === "") {
            mensaje_codigo_pnf.innerHTML = "";
            return;
        }

        await validar_codigo_pnf();
    });

    input_codigo_pnf.addEventListener("input", function () {
        this.value = this.value
            .toUpperCase()
            .replace(/[^A-Z0-9]/g, "")
            .slice(0, 8); 
    });
});