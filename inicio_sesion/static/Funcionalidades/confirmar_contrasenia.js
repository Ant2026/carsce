document.addEventListener("DOMContentLoaded", function () {

    const password = document.getElementById("confirmar_password");

    const icon_eye = document.getElementById("confirmar_mostrar_password");
    const icon_eye_off = document.getElementById("confirmar_ocultar_password");

    icon_eye.addEventListener("click", function () {
        password.type = "text";

        icon_eye.classList.add("d-none");
        icon_eye_off.classList.remove("d-none");
    });

    icon_eye_off.addEventListener("click", function () {
        password.type = "password";

        icon_eye_off.classList.add("d-none");
        icon_eye.classList.remove("d-none");
    });

    icon_eye_off.classList.add("d-none");
});