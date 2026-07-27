document.addEventListener("DOMContentLoaded", function () {
    const municipioSelect = document.getElementById("municipio_residencia");

    const municipios = ["Barinas", "Pedraza", "Antonio José de Sucre", "Ezequiel Zamora", "Bolívar", "Alberto Arvelo Torrealba", "Rojas", "Obispo", "Sosa", "Cruz Paredes", "Arismendi", "Andrés Eloy Blanco"];

    function cargarMunicipios() {
        municipioSelect.innerHTML = '<option disabled selected hidden>Elije una opción</option>';

        municipios.forEach(municipio => {
            const option = document.createElement("option");
            option.value = municipio;
            option.textContent = municipio;
            municipioSelect.appendChild(option);
        });
    }

    cargarMunicipios();
});
