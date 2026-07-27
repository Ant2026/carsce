document.addEventListener("DOMContentLoaded", function () {
    const campo_cedula2 = document.getElementById("cedula_identidad2");
    const select_nacionalidad2 = document.getElementById("nacionalidad2");

    function longitud_identidad2() {
        const nacionalidad = select_nacionalidad2.value;

        if (nacionalidad === "") {

            campo_cedula2.value = "";
            campo_cedula2.disabled = true;
            campo_cedula2.placeholder = "Seleccione nacionalidad";
            return;
        }

        campo_cedula2.removeAttribute("minLength");
        campo_cedula2.removeAttribute("maxLength");


        switch (nacionalidad) {
            case "V":
                campo_cedula2.disabled = false;
                campo_cedula2.maxLength = 8;
                campo_cedula2.minLength = 7;
                campo_cedula2.placeholder = "Cédula de Identidad (7-8)";
                break;
            case "E":
                campo_cedula2.disabled = false;
                campo_cedula2.maxLength = 10;
                campo_cedula2.minLength = 8;
                campo_cedula2.placeholder = "Pasaporte/DNI (8-10)";
                break;
        }
    }

    campo_cedula2.addEventListener("input", function () {
        this.value = this.value.replace(/\D/g, "");
    });

    select_nacionalidad2.addEventListener("change", longitud_identidad2);

    longitud_identidad2();

    const campo_cedula3 = document.getElementById("cedula_identidad3");
    const select_nacionalidad3 = document.getElementById("nacionalidad3");

    function longitud_identidad3() {
        const nacionalidad = select_nacionalidad3.value;

        if (nacionalidad === "") {

            campo_cedula3.value = "";
            campo_cedula3.disabled = true;
            campo_cedula3.placeholder = "Seleccione nacionalidad";
            return;
        }

        campo_cedula3.removeAttribute("minLength");
        campo_cedula3.removeAttribute("maxLength");

        switch (nacionalidad) {
            case "V":
                campo_cedula3.disabled = false;
                campo_cedula3.maxLength = 8;
                campo_cedula3.minLength = 7;
                campo_cedula3.placeholder = "Cédula de Identidad (7-8)";
                break;
            case "E":
                campo_cedula3.disabled = false;
                campo_cedula3.maxLength = 10;
                campo_cedula3.minLength = 8;
                campo_cedula3.placeholder = "Pasaporte/DNI (8-10)";
                break;
        }
    }

    campo_cedula3.addEventListener("input", function () {
        this.value = this.value.replace(/\D/g, "");
    });

    select_nacionalidad3.addEventListener("change", longitud_identidad3);

    longitud_identidad3();
});