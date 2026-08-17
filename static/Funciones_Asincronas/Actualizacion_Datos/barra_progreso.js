document.addEventListener("DOMContentLoaded", () => {


    const pasos = document.querySelectorAll(".paso_formulario");

    console.log("Cantidad de pasos:", pasos.length);

    pasos.forEach((paso, index) => {
        console.log(index, paso.id, paso.className);
    });

    const barra = document.querySelectorAll(".paso_barra");


    const btnAnterior = document.getElementById("btn_anterior");

    const btnSiguiente = document.getElementById("btn_siguiente");

    const btnRegistro = document.getElementById("btn_registro");


    let pasoActual = 0;



    function mostrarPaso(index) {


        pasos.forEach((paso, i) => {

            paso.classList.remove("activo");


            if (i === index) {

                paso.classList.add("activo");

            }

        });



        barra.forEach((item, i) => {


            item.classList.remove("activo");


            if (i < index) {

                item.classList.add("completado");

            }
            else {

                item.classList.remove("completado");

            }


            if (i === index) {

                item.classList.add("activo");

            }


        });



        // controlar botones


        btnAnterior.style.display =
            index === 0 ? "none" : "block";



        btnSiguiente.style.display =
            index === pasos.length - 1 ? "none" : "block";



        btnRegistro.style.display =
            index === pasos.length - 1 ? "block" : "none";


    }

    function validarPasoActual() {

        const paso = pasos[pasoActual];

        const campos = paso.querySelectorAll(
            "input, select, textarea"
        );

        let valido = true;
        let primerCampo = null;

        campos.forEach(campo => {

            if (
                campo.hasAttribute("required") &&
                !campo.value.trim()
            ) {

                campo.classList.add("error");

                if (!primerCampo) {
                    primerCampo = campo;
                }

                valido = false;

            } else {

                campo.classList.remove("error");

            }

        });

        if (primerCampo) {
            primerCampo.focus();
        }

        return valido;

    }


    btnSiguiente.addEventListener("click", () => {

        if (!validarPasoActual()) {

            Swal.fire({
                title: "Campos incompletos",
                text: "Debe completar todos los campos obligatorios antes de continuar.",
                icon: "warning",
                confirmButtonText: "Entendido",
                confirmButtonColor: "#2563eb",
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            return;
        }

        pasoActual++;

        mostrarPaso(pasoActual);

    });



    btnAnterior.addEventListener("click", () => {
        if (pasoActual > 0) {
            pasoActual--;
            mostrarPaso(pasoActual);
        }
    });

    document.querySelectorAll("input, select, textarea").forEach(campo => {

        campo.addEventListener("input", () => {
            campo.classList.remove("error");
        });

        campo.addEventListener("change", () => {
            campo.classList.remove("error");
        });

    });

    mostrarPaso(pasoActual);

});