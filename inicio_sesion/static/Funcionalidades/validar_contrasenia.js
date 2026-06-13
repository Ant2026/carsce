document.addEventListener("DOMContentLoaded", function(){

    const formulario = document.querySelector("form");
    const password = document.getElementById("password");
    const barra = document.getElementById("nivel_password");
    const texto = document.getElementById("texto_password");

    password.addEventListener("input", function(){
        const valor = password.value;
        const tiene_longitud = valor.length >= 8;
        const tiene_mayuscula = /[A-Z]/.test(valor);
        const tiene_minuscula = /[a-z]/.test(valor);
        const tiene_numero = /[0-9]/.test(valor);
        const tiene_especial = /[!@#$%^&*(),.?":{}|<>]/.test(valor);

        let fuerza = 0;

        if(tiene_longitud) fuerza++;
        if(tiene_mayuscula) fuerza++;
        if(tiene_minuscula) fuerza++;
        if(tiene_numero) fuerza++;
        if(tiene_especial) fuerza++;

        if(fuerza <= 2){
            password_segura = false;
            barra.style.width = "33%";
            barra.style.background = "#ef4444";
            texto.textContent = "Contraseña débil";
            texto.style.color = "#ef4444";

        } else if(fuerza <= 4){
            password_segura = false;
            barra.style.width = "66%";
            barra.style.background = "#f59e0b";
            texto.textContent = "Contraseña intermedia";
            texto.style.color = "#f59e0b";

        } else {
            password_segura = true;
            barra.style.width = "100%";
            barra.style.background = "#22c55e";
            texto.textContent = "Contraseña segura";
            texto.style.color = "#22c55e";
        }

        if(valor.length === 0){

            password_segura = false;
            barra.style.width = "0%";
            texto.textContent = "Seguridad de la contraseña";
            texto.style.color = "#000";
        }
    });

    formulario.addEventListener("submit", function(){

        barra.style.width = "0%";
        texto.textContent = "Seguridad de la contraseña";
        texto.style.color = "#000";

        password_segura = false;
    });

});