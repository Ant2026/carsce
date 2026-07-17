document.addEventListener("DOMContentLoaded", () => {

    const formulario_registro = document.getElementById("formulario_registrar_trayectos")
    const contenedor_trayectos = document.getElementById("trayectos_registrados")

    const campoTrayecto = document.getElementById("trayecto_registrar");

    async function siguienteTrayecto() {
        try {
            const respuesta = await fetch("/siguiente_trayecto/");
            const resultado = await respuesta.json();
            if (resultado.estado === "fallo") {
                Swal.fire({
                    icon: resultado.icon,
                    text: resultado.descripcion
                });
                return;
            }
            campoTrayecto.value = resultado.trayecto;
        } catch (error) {
            console.error(error);
        }
    }
    siguienteTrayecto();

    formulario_registro.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registro)

            const respuesta = await fetch("/modulo_trayecto/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json()

            await siguienteTrayecto()
            await trayectos_registrados()

            Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                allowOutsideClick: false,
                allowEscapeKey: false
            });
            
        } catch (error) {
            console.error(error)
        }
    });

    async function trayectos_registrados() {
        try {
            const respuesta = await fetch("/trayectos_registrados/");
            const resultado = await respuesta.json();

            contenedor_trayectos.innerHTML = "";

            resultado.trayectos.forEach((trayecto, index) => {
                contenedor_trayectos.innerHTML += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${trayecto.trayecto}</td>
                    </tr>
                `;
            });
        } catch (error) {
            console.error(error);
        }
    }
    trayectos_registrados();
});