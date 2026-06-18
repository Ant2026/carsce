document.addEventListener("DOMContentLoaded", () => {

    const contenedor_pre_inscripcion = document.getElementById("contenedor_pre_inscripcion");

    async function estudiante_pre_inscripcion() {
        try {
            const respuesta = await fetch("/obtener_pre_inscripto/");
            const resultado = await respuesta.json();

            if (resultado.estado === "fallo") {
                Swal.fire({
                    title: resultado.titulo,
                    text: resultado.descripcion,
                    icon: resultado.icon
                });
                return;
            }

            contenedor_pre_inscripcion.innerHTML += `
                <tr>
                    <td>${resultado.id || ""}</td>
                    <td>${resultado.nombres}</td>
                    <td>${resultado.apellidos}</td>
                    <td>${resultado.cedula}</td>
                    <td colspan="3">
                        <form class="formulario_inscripcion">
                            <input type="hidden" name="cedula" value="${resultado.cedula}">
                            <button type="submit">
                                Inscribir
                            </button>
                        </form>
                    </td>
                </tr>
            `;

        } catch (error) {
            console.error(error);
        }
    }

    contenedor_pre_inscripcion.addEventListener("submit", async (e) => {
        if (!e.target.classList.contains("formulario_inscripcion")) return;

        e.preventDefault();

        const datos = new FormData(e.target);

        try {
            const respuesta = await fetch("/inscribir_estudiante/", {
                method: "POST",
                body: datos
            });

            const resultado = await respuesta.json();

            Swal.fire({
                title: resultado.titulo,
                text: resultado.descripcion,
                icon: resultado.icon
            });

        } catch (error) {
            console.error(error);
        }
    });

    estudiante_pre_inscripcion();

});