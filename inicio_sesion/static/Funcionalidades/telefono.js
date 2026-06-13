document.addEventListener("DOMContentLoaded", function () {

    const input_numerico_telefonico = document.getElementById("numero_telefonico");
    const select_prefijo_telefonico = document.getElementById("prefijo_telefono");

    const prefijos = ["0414", "0424", "0416", "0426", "0412", "0422"];

    function prefijos_select() {
        select_prefijo_telefonico.innerHTML = "<option disabled selected hidden>TLF</option>";
        input_numerico_telefonico.placeholder = "Número telefonico debe llevar 7 digitos";

        prefijos.forEach(prefijo => {
            const option = document.createElement("option");

            option.value = prefijo;
            option.textContent = prefijo;

            select_prefijo_telefonico.appendChild(option);

        });
    }

    prefijos_select();

    select_prefijo_telefonico.addEventListener("change", function () {
        input_numerico_telefonico.value = "";
        input_numerico_telefonico.disabled = false;        
    });

    input_numerico_telefonico.addEventListener("keydown", function (e) {
        const caracter = e.key;

        const teclas_permitidas = [
            "Backspace",
            "ArrowLeft",
            "ArrowRight",
            "Delete",
            "Tab"
        ];

        if (teclas_permitidas.includes(caracter)) {
            return;
        }

        if (!/^\d$/.test(caracter)) {
            e.preventDefault();
            return;
        }

        if (input_numerico_telefonico.value.length >= 7) {
            e.preventDefault();
            return;
        }

    });

    input_numerico_telefonico.addEventListener("paste", function (e) {
        e.preventDefault();
    });

});