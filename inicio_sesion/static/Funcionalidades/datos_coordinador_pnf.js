document.addEventListener("DOMContentLoaded", () => {
    const selects_nucleos = document.getElementById("selects_nucleos")
    const selects_pnfs = document.getElementById("selects_pnfs")

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    async function nucleos_asignados() {
        try {
            const respuesta = await fetch("/nucleos_coordinador_pnfs/")
            const resultado = await respuesta.json()

            selects_nucleos.innerHTML = '<option disabled selected hidden>Elije el Núcleo</option>'

            resultado.nucleos.forEach(nucleo => {
                const option = document.createElement("option")

                option.value = nucleo.id_nucleo
                option.textContent = nucleo.municipio

                selects_nucleos.appendChild(option)
            });
        } catch (error) {
            console.error(error)
        }
    }
    nucleos_asignados();

    selects_nucleos.addEventListener("change", async function (e) {
        e.preventDefault()
        selects_pnfs.disabled = false
        try {
            const formulario = new FormData()
            formulario.append("nucleo", selects_nucleos.value)

            const respuesta = await fetch("/pnfs_coordinador_pnfs/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formulario
            })
            const resultado = await respuesta.json()

            selects_pnfs.innerHTML = '<option disabled selected hidden>Elije el PNF</option>'

            resultado.pnfs.forEach(pnf => {
                const option = document.createElement("option")

                option.value = pnf.id_pnf
                option.textContent = pnf.pnf

                selects_pnfs.appendChild(option)
            });
        } catch (error) {
            console.error(error)
        }
    }); 


});