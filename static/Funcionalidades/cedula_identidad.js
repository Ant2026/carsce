function configurarCedula(selectNacionalidad, campoCedula) {

    function longitudIdentidad() {
        const nacionalidad = selectNacionalidad.value;

        campoCedula.value = "";

        if (nacionalidad === "") {
            campoCedula.disabled = true;
            campoCedula.placeholder = "Seleccione nacionalidad";
            return;
        }

        campoCedula.disabled = false;

        switch (nacionalidad) {
            case "V":
                campoCedula.maxLength = 8;
                campoCedula.minLength = 7;
                campoCedula.placeholder = "Cédula de Identidad (7-8)";
                break;

            case "E":
                campoCedula.maxLength = 10;
                campoCedula.minLength = 8;
                campoCedula.placeholder = "Pasaporte/DNI (8-10)";
                break;
        }
    }

    campoCedula.addEventListener("input", function () {
        this.value = this.value.replace(/\D/g, "");
    });

    selectNacionalidad.addEventListener("change", longitudIdentidad);

    longitudIdentidad();
}