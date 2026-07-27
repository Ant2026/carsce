document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("id_clave");
    const wrapper = document.createElement("div");

    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.gap = "10px";

    passwordInput.parentNode.insertBefore(wrapper, passwordInput);

    wrapper.appendChild(passwordInput);

    const toggleButton = document.createElement("span");

    toggleButton.innerHTML = '<i class="fas fa-eye"></i>';

    toggleButton.style.cursor = "pointer";
    toggleButton.style.fontSize = "18px";

    wrapper.appendChild(toggleButton);

    toggleButton.addEventListener("click", function () {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            toggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordInput.type = "password";
            toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });
});