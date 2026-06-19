document.addEventListener("DOMContentLoaded", () => {

    const boton = document.getElementById("btn_discapacidad");
    const campos = document.getElementById("campos_discapacidad");

    boton.addEventListener("click", () => {

        campos.classList.toggle("activo");

        if (campos.classList.contains("activo")) {
            boton.textContent = "Ocultar";
        } else {
            boton.textContent = "Mostrar";
        }

    });

});