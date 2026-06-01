document.addEventListener("DOMContentLoaded", () => {

    const btnReenviar = document.getElementById("btn_reenviar_codigo");
    const contador = document.getElementById("contador_reenvio");

    if (!btnReenviar || !contador) return;

    let tiempo = 60;

    btnReenviar.disabled = true;

    const intervalo = setInterval(() => {
        tiempo--;

        contador.textContent = tiempo;

        if (tiempo <= 0) {
            clearInterval(intervalo);
            btnReenviar.disabled = false;
            contador.textContent = "";
            btnReenviar.textContent = "Reenviar código";
        }
    }, 1000);

    btnReenviar.addEventListener("click", async () => {
        btnReenviar.disabled = true;

        try {
            const resp = await fetch("/reenviar_codigo_btn/");
            const data = await resp.json();

            await Swal.fire({
                icon: data.icon || "info",
                text: data.descripcion
            });
            location.reload();

        } catch (error) {
            Swal.fire({
                icon: "error",
                text: "Error al reenviar el código"
            });

            btnReenviar.disabled = false;
        }
    });

});