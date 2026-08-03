document.addEventListener("DOMContentLoaded", () => {

    const input_date_Inicial_Trimestre = document.getElementById("fecha_Inicial_Trimestral");
    const input_date_Inicial_Semestre = document.getElementById("fecha_Inicial_Semestral");
    const input_date_Reparacion = document.getElementById("fecha_Reparacion");
    const input_date_TramoI = document.getElementById("fecha_TramoI");
    const input_date_TramoII = document.getElementById("fecha_TramoII");
    const input_date_TramoIII = document.getElementById("fecha_TramoIII");
    const input_date_SemestreI = document.getElementById("fecha_SemestreI");
    const input_date_SemestreII = document.getElementById("fecha_SemestreII");

    const formulario_registrar = document.getElementById("registrar_calendario");

    function limitarMes(input, mes) {

        const anio = new Date().getFullYear();
        const ultimoDia = new Date(anio, mes, 0).getDate();

        input.min = `${anio}-${String(mes).padStart(2, "0")}-01`;
        input.max = `${anio}-${String(mes).padStart(2, "0")}-${String(ultimoDia).padStart(2, "0")}`;

        input.addEventListener("input", function () {

            if (!this.value) return;

            const fecha = new Date(this.value + "T00:00:00");
            const diaSemana = fecha.getDay();

            if (diaSemana === 0 || diaSemana === 6) {
                this.setCustomValidity("No puede seleccionar fines de semana.");
                this.reportValidity();
                this.value = "";
            } else {
                this.setCustomValidity("");
            }

        });
    }

    limitarMes(input_date_Inicial_Trimestre, 11);    
    limitarMes(input_date_Inicial_Semestre, 11);    
    limitarMes(input_date_Reparacion, 12); 
    limitarMes(input_date_TramoI, 4); 
    limitarMes(input_date_TramoII, 7);    
    limitarMes(input_date_TramoIII, 11); 
    limitarMes(input_date_SemestreI, 7); 
    limitarMes(input_date_SemestreII, 3); 

    formulario_registrar.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_registrar);

            const respuesta = await fetch("/reg_calendario/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);
            
            await Swal.fire({
                text: resultado.descripcion,
                icon: resultado.icon,
                title: resultado.title,
                allowOutsideClick: false,
                allowEscapeKey: false
            });

            if (resultado.estado == "exito") {
                formulario_registrar.reset();
            }
        } catch (error) {
            console.error(error)
        }
    });

});