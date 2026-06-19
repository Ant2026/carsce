document.addEventListener("DOMContentLoaded", () => {

    const fechaNacimiento = document.getElementById("fecha_nacimiento");

    const anio = new Date().getFullYear() - 18;

    fechaNacimiento.max = `${anio}-12-31`;

});