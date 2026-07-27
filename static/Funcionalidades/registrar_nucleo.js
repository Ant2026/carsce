document.addEventListener("DOMContentLoaded", () => {
    const dialogo = document.getElementById("dialogo_nucleos");
    const formulario_dialogo = document.getElementById("formulario_nucleos");

    const btn_nucleo = document.getElementById("mostrar_dialogo")
    const select_nucleo = document.getElementById("nucleos")

    if (mostrarDialogo) {
        dialogo.showModal();
    }

    formulario_dialogo.addEventListener("submit", async function (e) {
        e.preventDefault();

        try {
            const formulario = new FormData(formulario_dialogo);
            const respuesta = await fetch("", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            if (resultado.icon === "success") {
                dialogo.close();
                location.reload();
            }
        } catch (error) {
            console.error(error);
        }
    });

    btn_nucleo.addEventListener("click", function (e) {
        if (nucleoActual) {
            select_nucleo.value = nucleoActual;
        }
        dialogo.showModal();
    });
});