document.addEventListener("DOMContentLoaded", () => {
    const inputCodigo = document.getElementById("comprobar_codigo");
    const icon_eye = document.getElementById("mostrar_password");
    const icon_eye_off = document.getElementById("ocultar_password");

    icon_eye.addEventListener("click", () => {
        inputCodigo.type = "text";

        icon_eye.classList.add("d-none");
        icon_eye_off.classList.remove("d-none")
    });

    icon_eye_off.addEventListener("click", () => {
        inputCodigo.type = "password";

        icon_eye_off.classList.add("d-none");
        icon_eye.classList.remove("d-none");
    });
});