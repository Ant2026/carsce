document.addEventListener("DOMContentLoaded", function () {

    const input_correo = document.getElementById("Correo");
    const select_dominio_correo = document.getElementById("dominio");

    input_correo.addEventListener("keydown", function (e) {
        
        let caracter = e.key;

        let caracteres_denegado = [
            "@", "com", "net", "edu", "gov", "org", "ve", "es", "ar", "mx",
            " ", "(", ")", "[", "]", "{", "}", "<", ">", ",", ";", ":", "\\", "/",
            "'", "\"", "|", "°", "¬", "¿", "?", "¡", "!", "#", "$", "%", "^", "&",
            "*", "=", "+", "~", "`", "-", "´"
        ];

        /* Bloquear caracteres no permitidos */
        if (caracteres_denegado.includes(caracter)) {

            e.preventDefault();
            return;
        }

        /* Permitir solo un punto */
        if (caracter === "." && input_correo.value.includes(".")) {

            e.preventDefault();
            return;
        }

        /* Evitar punto al inicio */
        if (caracter === "." && input_correo.value.length === 0) {

            e.preventDefault();
            return;
        }

    });

    function DominioSelect() {
        
        const dominios = [
            "@gmail.com",
            "@outlook.com",
            "@yahoo.com"
        ];

        select_dominio_correo.innerHTML = "<option disabled selected hidden>DOMINIO</option>";
        input_correo.placeholder = "Nombre del correo electronico";

        dominios.forEach(dominio => {

            const option = document.createElement("option");

            option.value = dominio;
            option.textContent = dominio;

            select_dominio_correo.appendChild(option);

        });
    }

    DominioSelect();

    input_correo.addEventListener("paste", function (e) {
        e.preventDefault();
        return;
    });

});