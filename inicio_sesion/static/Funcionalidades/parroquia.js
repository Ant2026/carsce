document.addEventListener("DOMContentLoaded", function () {
    
    const municipioSelect = document.getElementById("municipio_residencia");
    const parroquiaSelect = document.getElementById("parroquia_residencia");
    const direccionTextarea = document.getElementById("direccion_domicilio");

    const parroquiasPorMunicipio = {
        "Barinas": ["Alfredo Arvelo Larriva", "San Silvestre", "Santa Inés", "Santa Lucía", "Torunos", "El Carmen", "Alto Barinas", "Rómulo Betancourt", "Corazón de Jesús", "Ramón Ignacio Méndez", "Manuel Palacio Fajardo", "Juan Antonio Rodríguez Domínguez", "Domingo Ortiz de Páez"],

        "Pedraza": ["Ciudad Bolivia", "Ignacio Briceño", "José Félix Ribas", "Páez"],

        "Antonio José de Sucre": ["Ticoporo", "Andrés Bello", "Nicolás Pulido"],

        "Ezequiel Zamora": ["Santa Bárbara", "José Ignacio del Pumar", "Pedro Briceño Méndez", "Ramón Ignacio Méndez"],

        "Bolívar": ["Barinitas", "Altamira de Cáceres", "Calderas"],

        "Alberto Arvelo Torrealba": ["Sabaneta", "El Real"],

        "Rojas": ["Libertad", "Dolores", "Palacios Fajardo", "Santa Rosa", "Simón Rodríguez"],

        "Obispo": ["Obispos", "El Real", "La Luz", "Los Guasimitos"],

        "Sosa": ["Ciudad de Nutrias", "El Regalo", "Puerto de Nutrias", "Santa Catalina", "Simón Bolívar"],

        "Cruz Paredes": ["Barrancas", "El Socorro", "Masparrito"],

        "Arismendi": ["Arismendi", "Guadarrama", "La Unión", "San Antonio"],

        "Andrés Eloy Blanco": ["El Cantón", "Santa Cruz de Guacas", "Puerto Vivas", "Dominga Ortiz de Páez"]
    };

    function actualizarParroquias() {
        const municipio = municipioSelect.value;

        // Limpiar parroquias
        parroquiaSelect.innerHTML = '<option disabled selected hidden>Elije una opción</option>';

        if (municipio in parroquiasPorMunicipio) {
            parroquiasPorMunicipio[municipio].forEach(parroquia => {
                const option = document.createElement("option");
                option.value = parroquia;
                option.textContent = parroquia;
                parroquiaSelect.appendChild(option);
            });

            parroquiaSelect.disabled = false;
            direccionTextarea.disabled = false;
        } else {
            parroquiaSelect.disabled = true;
            direccionTextarea.disabled = true;
        }
    }

    municipioSelect.addEventListener("change", actualizarParroquias);
});
