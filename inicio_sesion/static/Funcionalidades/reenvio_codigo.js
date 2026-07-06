document.addEventListener("DOMContentLoaded", () => {

    const btnReenviar = document.getElementById("btn_reenviar_codigo");
    const contador = document.getElementById("contador_reenvio");

    if (!btnReenviar || !contador) return;

    const DURACION = 60;

    function iniciarContador() {

        const inicio = localStorage.getItem("inicio_reenvio");

        if (!inicio) {
            btnReenviar.disabled = false;
            return;
        }

        btnReenviar.disabled = true;

        const intervalo = setInterval(() => {

            const transcurrido = Math.floor(
                (Date.now() - parseInt(inicio)) / 1000
            );

            const restante = DURACION - transcurrido;

            if (restante <= 0) {

                clearInterval(intervalo);

                btnReenviar.disabled = false;
                contador.textContent = "";

                localStorage.removeItem("inicio_reenvio");

                return;
            }

            contador.textContent = restante;

        }, 1000);

    }

    iniciarContador();

    btnReenviar.addEventListener("click", async () => {
        btnReenviar.disabled = true;
        try {
            const resp = await fetch("/reenviar_codigo_btn/");
            const data = await resp.json();

            await Swal.fire({
                icon: data.icon || "info",
                text: data.descripcion
            });

            localStorage.setItem("inicio_reenvio", Date.now());

            location.reload();
        } catch (error) {
            btnReenviar.disabled = false;
            Swal.fire({
                icon: "error",
                text: "Error al reenviar el código"
            });
        }

    });

});