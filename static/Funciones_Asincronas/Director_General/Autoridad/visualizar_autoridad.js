document.addEventListener("DOMContentLoaded", () => {

    const formulario_actualizar = document.getElementById("formulario_actualizar_autoridades");

    const contenedor_autoridades = document.getElementById("contenedor_autoridades");

    async function obtener_autoridades() {
        try {
            const respuesta = await fetch("/auts_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);

            contenedor_autoridades.innerHTML = "";

            resultado.forEach(autoridad => {
                contenedor_autoridades.innerHTML += `
                    <tr>
                        <td>${autoridad.nombres}</td>
                        <td>${autoridad.apellidos}</td>
                        <td>${autoridad.cedula_identidad}</td>
                        <td>${autoridad.cargo}</td>
                        <td>${autoridad.resolucion}</td>
                    </tr>
                `;
            });

        } catch (error) {
            console.error(error)
        }
    }
    obtener_autoridades();
});