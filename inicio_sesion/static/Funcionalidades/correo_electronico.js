document.addEventListener("DOMContentLoaded", function () {

    const input_correo = document.getElementById("Correo");
    const select_dominio_correo = document.getElementById("dominio");

    input_correo.addEventListener("keydown", function (e) {
        let caracter = e.key;
        let caracteres_denegado = ["@", "com", "net", "edu", "gov", "org", "ve", "es", "ar", "mx",
            " ", "(", ")", "[", "]", "{", "}", "<", ">", ",", ";", ":", "\\", "/",
            "'", "\"", "|", "°", "¬", "¿", "?", "¡", "!", "#", "$", "%", "^", "&",
            "*", "=", "+", "~", "`", "-", "´"];

        if (caracteres_denegado.includes(caracter)) {
            e.preventDefault();
            return;
        }
    });

    function DominioSelect() {
        const dominios = ["@gmail.com", "@outlook.com", "@yahoo.com"];

        select_dominio_correo.innerHTML = "<option disabled selected hidden>DOMINIO</option>";
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