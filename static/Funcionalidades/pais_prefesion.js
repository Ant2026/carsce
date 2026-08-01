function cargarPaises(select) {

    const paises = [
        "Venezuela",
        "Colombia",
        "Perú",
        "Ecuador",
        "Chile",
        "Brasil",
        "Panamá",
        "República Dominicana",
        "Argentina",
        "México",
        "Estados Unidos",
        "Canadá",
        "España",
        "Italia",
        "Portugal",
        "Francia",
        "Alemania",
        "Reino Unido"
    ];

    if (!select) return;

    select.innerHTML = "<option value=''>Elije una opción</option>";

    paises.forEach(pais => {
        const option = document.createElement("option");
        option.value = pais;
        option.textContent = pais;
        select.appendChild(option);
    });
}