document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("id_clave");

    if (!input) return;

    const icono = document.createElement("i");
    icono.id = "toggleClave";
    icono.className = "icon-eye";

    input.parentNode.style.position = "relative";
    input.parentNode.appendChild(icono);

    icono.addEventListener("click", () => {
        if (input.type === "password") {
            input.type = "text";
            icono.classList.replace("icon-eye", "icon-eye-off");
        } else {
            input.type = "password";
            icono.classList.replace("icon-eye-off", "icon-eye");
        }
    });
});