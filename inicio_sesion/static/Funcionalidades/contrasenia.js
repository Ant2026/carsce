document.addEventListener("DOMContentLoaded", function () {
    const eyeOff = document.querySelector(".eye_off");
    const eyeOn = document.querySelector(".eye_on");
    const toggleCheck = document.getElementById("oculta_aparecer");
    const inputPassword = document.getElementById("password");

    function actualizarIconoYPassword() {
        if (toggleCheck.checked) {
            inputPassword.type = "text";   // mostrar contraseña
            eyeOff.classList.add("ocultar");
            eyeOn.classList.remove("ocultar");
        } else {
            inputPassword.type = "password"; // ocultar contraseña
            eyeOn.classList.add("ocultar");
            eyeOff.classList.remove("ocultar");
        }
    }

    toggleCheck.addEventListener("change", actualizarIconoYPassword);

    // Estado inicial
    actualizarIconoYPassword();
});