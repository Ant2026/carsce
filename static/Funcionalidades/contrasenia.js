document.addEventListener("DOMContentLoaded", function () {
    const eyeOn = document.querySelector(".icon-eye");
    const eyeOff = document.querySelector(".icon-eye-off");
    const toggleCheck = document.getElementById("oculta_aparecer");
    const inputPassword = document.getElementById("password");

    function actualizarIconoYPassword() {
        if (toggleCheck.checked) {
            inputPassword.type = "text";  
            eyeOff.classList.add("ocultar");
            eyeOn.classList.remove("ocultar");
        } else {
            inputPassword.type = "password"; 
            eyeOn.classList.add("ocultar");
            eyeOff.classList.remove("ocultar");
        }
    }

    toggleCheck.addEventListener("change", actualizarIconoYPassword);

    actualizarIconoYPassword();
});