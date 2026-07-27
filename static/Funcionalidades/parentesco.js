document.addEventListener("DOMContentLoaded", () => {

    const parentescos = [
        "Madre",
        "Padre",
        "Tutor",
        "Abuelo/a",
        "Hermano/a"
    ];

    function llenarSelect(id) {
        const select = document.getElementById(id);

        select.innerHTML = `<option value="">Seleccione</option>`;

        parentescos.forEach(p => {
            const option = document.createElement("option");
            option.value = p;
            option.textContent = p;
            select.appendChild(option);
        });
    }

    // llenar ambos selects
    llenarSelect("parestenco");
    llenarSelect("otroparestenco");

    // mostrar segundo representante
    const btn = document.getElementById("btn_otro_representante");
    const sub = document.getElementById("subcontenedor_representante");

    btn.addEventListener("click", () => {

        const visible = sub.style.display === "block";

        sub.style.display = visible ? "none" : "block";

        btn.textContent = visible
            ? "Agregar segundo representante"
            : "Quitar segundo representante";

    });

});