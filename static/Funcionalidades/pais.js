document.addEventListener("DOMContentLoaded", function () {
    const pais_profesion = document.getElementById("pais_profesion");

    const Paises = ["Venezuela", "Colombia", "Perú ", "Ecuador ", "Chile ", "Brasil ", "Panamá ", "República Dominicana",
        "Argentina ", "México ", "Estados Unidos", "Canadá ", "España ", "Italia", "Portugal ",
        "Francia", "Alemania", "Reino Unido"];

    function pais_proefesion_personal() {
        pais_profesion.innerHTML = "<option disabled selected hidden>Elije una opción</option>";

        Paises.forEach(codigo => {
            const option = document.createElement("option");
            option.value = codigo;
            option.textContent = codigo;
            pais_profesion.appendChild(option);
        });
    }
    pais_proefesion_personal();
});