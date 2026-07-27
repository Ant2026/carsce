document.addEventListener("DOMContentLoaded", () => {

    const input_correo_num2 = document.getElementById("Correo_num2");
    const select_dominio_correo_num2 = document.getElementById("dominio_num2");

    const input_correo_num3 = document.getElementById("Correo_num3");
    const select_dominio_correo_num3 = document.getElementById("dominio_num3");

    function DominioSelect(select, input) {

        const dominios = [
            "@gmail.com",
            "@outlook.com",
            "@yahoo.com"
        ];

        select.innerHTML = "<option disabled selected hidden>DOMINIO</option>";
        input.placeholder = "Nombre del correo electronico";

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

    DominioSelect(select_dominio_correo_num2, input_correo_num2);
    DominioSelect(select_dominio_correo_num3, input_correo_num3);

    ValidarCorreo(input_correo_num2);
    ValidarCorreo(input_correo_num3);

});