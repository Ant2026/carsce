document.addEventListener("DOMContentLoaded", function () {

    const prefijos = ["0414", "0424", "0416", "0426", "0412", "0422"];

    function llenar(select) {
        if (!select) return;

        select.innerHTML = "<option disabled selected hidden>TLF</option>";

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

    const input2 = document.getElementById("numero_telefonico2");
    const select2 = document.getElementById("prefijo_telefono2");

    llenar(select2);
    validar(input2);

    if (select2 && input2) {
        select2.addEventListener("change", function () {
            input2.value = "";
            input2.disabled = false;
        });
    }

    const input3 = document.getElementById("numero_telefonico3");
    const select3 = document.getElementById("prefijo_telefono3");

    llenar(select3);
    validar(input3);

    if (select3 && input3) {
        select3.addEventListener("change", function () {
            input3.value = "";
            input3.disabled = false;
        });
    }

});