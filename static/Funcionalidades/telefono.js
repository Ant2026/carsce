function configurarTelefono(inputTelefono, selectPrefijo) {

    const prefijos = ["0414", "0424", "0416", "0426", "0412", "0422"];

    function cargarPrefijos() {

        selectPrefijo.innerHTML = "<option value='' selected>TLF</option>";

        inputTelefono.placeholder = "Número telefónico debe llevar 7 dígitos";

        prefijos.forEach(prefijo => {
            const option = document.createElement("option");
            option.value = prefijo;
            option.textContent = prefijo;
            selectPrefijo.appendChild(option);
        });

    }

    selectPrefijo.addEventListener("change", function () {
        inputTelefono.value = "";

        if (this.value === "") {
            return;
        }

        inputTelefono.focus();
    });

    inputTelefono.addEventListener("keydown", function (e) {
        const tecla = e.key;

        const teclasPermitidas = [
            "Backspace",
            "Delete",
            "ArrowLeft",
            "ArrowRight",
            "Tab",
            "Home",
            "End"
        ];

        if (teclasPermitidas.includes(tecla)) {
            return;
        }

        if (!/^\d$/.test(tecla)) {
            e.preventDefault();
            return;
        }

        if (this.value.length >= 7) {
            e.preventDefault();
        }
    });

    inputTelefono.addEventListener("paste", function (e) {
        e.preventDefault();
    });

    cargarPrefijos();
}