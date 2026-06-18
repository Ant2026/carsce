document.addEventListener("DOMContentLoaded", () => {
    const contenedor_pnfs = document.getElementById("contenedor_pnfs")

    async function pnfs() {
        try {
            const respuesta = await fetch("/mostrar_pnfs_cursar/");
            const resultado = await respuesta.json();
            contenedor_pnfs.innerHTML = "";

            resultado.pnfs.forEach(pnf => {
                const div = document.createElement("div");

                const input = document.createElement("input");
                input.type = "checkbox";
                input.name = "pnfs";
                input.value = pnf.id;
                input.id = `pnf_${pnf.id}`;

                const label = document.createElement("label");
                label.htmlFor = input.id;
                label.textContent = pnf.nombre;
            
                div.appendChild(input);
                div.appendChild(label);

                contenedor_pnfs.appendChild(div);
            });
        } catch (error) {
            console.error(error);
        }
    }
    pnfs()
});