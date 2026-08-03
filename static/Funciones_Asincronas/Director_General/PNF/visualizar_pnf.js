document.addEventListener("DOMContentLoaded", async () => {
    
    const contenedor_tablas_pnfs = document.getElementById("tabla_pnfs");
    const tbody = document.getElementById("pnfs_registrados");

    async function cargar() {
        try {
            const respuesta = await fetch("/pnfs_reg/");
            const resultado = await respuesta.json();
            console.log(resultado);
            
            tbody.innerHTML = "";
            if (resultado.nucleos.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4">No hay PNFs registrados.</td>
                    </tr>
                `;
                return;
            }

            const nucleo = resultado.nucleos[0];
            nucleo.pnfs.forEach((pnf, index) => {
                tbody.innerHTML += `
                    <tr 
                        data-id-nucleo="${nucleo.id_nucleo}" 
                        data-id-pnf="${pnf.id_pnf}"
                    >
                        <td>${index + 1}</td>
                        <td>${pnf.pnf}</td>
                        <td>${pnf.codigo}</td>
                        <td>${pnf.periodo_academico}</td>
                    </tr>
                `;
            });
        } catch (error) {
            console.error(error);
        }
    }
    cargar();

});