export const input_numerico_telefonico = document.getElementById("numero_telefonico");
export const select_prefijo_telefonico = document.getElementById("prefijo_telefono");

document.addEventListener("DOMContentLoaded", function () {

    const prefijos = ["0414", "0424", "0416", "0426", "0412", "0422"];

    function prefijos_select() {
        select_prefijo_telefonico.innerHTML = "<option disabled selected hidden>TLF</option>";

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

});

