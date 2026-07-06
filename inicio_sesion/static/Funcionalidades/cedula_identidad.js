document.addEventListener("DOMContentLoaded", function () {
    const campo_cedula = document.getElementById("cedula_identidad");
    const select_nacionalidad = document.getElementById("nacionalidad");

    function longitud_identidad() {
        const nacionalidad = select_nacionalidad.value;

        if (nacionalidad === "") {

            campo_cedula.value = "";
            campo_cedula.disabled = true;
            campo_cedula.placeholder = "Seleccione nacionalidad";
            return;
        }

        campo_cedula.removeAttribute("minLength");
        campo_cedula.removeAttribute("maxLength");

        switch (nacionalidad) {
            case "V":
                campo_cedula.disabled = false;
                campo_cedula.maxLength = 8;
                campo_cedula.minLength = 7;
                campo_cedula.placeholder = "Cédula de Identidad (7-8)";
                break;
            case "E":
                campo_cedula.disabled = false;
                campo_cedula.maxLength = 10;
                campo_cedula.minLength = 8;
                campo_cedula.placeholder = "Pasaporte/DNI (8-10)";
                break;
        }
    }

    campo_cedula.addEventListener("input", function () {
        this.value = this.value.replace(/\D/g, "");
    });

    select_nacionalidad.addEventListener("change", longitud_identidad);

    longitud_identidad();
});