document.addEventListener("DOMContentLoaded", () => {
    /*=========================================
        FECHA AUTOMÁTICA
    =========================================*/

    const fecha = document.querySelector(".fecha_dashboard span");

    if (fecha) {

        const hoy = new Date();

        const opciones = {
            day: "numeric",
            month: "long",
            year: "numeric"
        };

        fecha.textContent = hoy.toLocaleDateString("es-ES", opciones);

    }


    /*=========================================
        CONTADORES
    =========================================*/

    const numeros = document.querySelectorAll(".card_info h2");

    numeros.forEach(numero => {

        const objetivo = parseInt(
            numero.textContent.replace(/,/g, "")
        );

        let actual = 0;

        const incremento = Math.ceil(objetivo / 80);

        const contador = setInterval(() => {

            actual += incremento;

            if (actual >= objetivo) {

                actual = objetivo;
                clearInterval(contador);

            }

            numero.textContent = actual.toLocaleString();

        }, 20);

    });


    /*=========================================
        ANIMACIÓN DE ENTRADA
    =========================================*/

    const elementos = document.querySelectorAll(
        ".card, .actividad, .grafico, .botones a"
    );

    elementos.forEach((elemento, indice) => {

        elemento.style.opacity = "0";
        elemento.style.transform = "translateY(30px)";

        setTimeout(() => {

            elemento.style.transition = ".6s ease";

            elemento.style.opacity = "1";
            elemento.style.transform = "translateY(0px)";

        }, indice * 120);

    });


    /*=========================================
GRÁFICO DE ESTUDIANTES POR NÚCLEO
=========================================*/

    const canvas = document.getElementById("grafico_dashboard");

    if (canvas) {

        const scriptElement = document.getElementById(
            "datos-nucleos-json"
        );

        let etiquetas = [];
        let valores = [];

        /*-----------------------------------------
            LEER DATOS DE DJANGO
        -----------------------------------------*/

        if (scriptElement) {

            try {

                const datosRaw = JSON.parse(
                    scriptElement.textContent.trim()
                );

                console.log("Datos recibidos desde Django:", datosRaw);

                etiquetas = datosRaw.map(item => item.nucleo);

                valores = datosRaw.map(item => Number(item.total));

                console.log("Etiquetas:", etiquetas);
                console.log("Valores:", valores);

            } catch (error) {

                console.error(
                    "Error al procesar los datos de estudiantes:",
                    error
                );

            }

        }


        /*-----------------------------------------
            SI NO HAY DATOS
        -----------------------------------------*/

        if (etiquetas.length === 0) {

            etiquetas = ["Sin datos"];

            valores = [0];

        }


        /*-----------------------------------------
            CREAR GRÁFICO
        -----------------------------------------*/

        new Chart(canvas, {

            type: "bar",

            data: {

                labels: etiquetas,

                datasets: [

                    {

                        label: "Estudiantes",

                        data: valores,

                        backgroundColor: "#2563EB",

                        borderRadius: 10,

                        borderSkipped: false

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        display: false

                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                return `Estudiantes: ${context.raw}`;

                            }

                        }

                    }

                },

                scales: {

                    x: {

                        grid: {

                            display: false

                        }

                    },

                    y: {

                        beginAtZero: true,

                        suggestedMax: function (context) {

                            const valores = context.chart.data.datasets[0].data;

                            const maximo = Math.max(...valores, 0);

                            if (maximo <= 5) {
                                return 5;
                            }

                            if (maximo <= 10) {
                                return 10;
                            }

                            if (maximo <= 50) {
                                return Math.ceil(maximo * 1.2);
                            }

                            if (maximo <= 100) {
                                return Math.ceil(maximo * 1.15);
                            }

                            return Math.ceil(maximo * 1.10);

                        },

                        ticks: {

                            precision: 0,

                            callback: function (value) {
                                return value.toLocaleString();
                            }

                        },

                        grid: {
                            color: "#ECECEC"
                        }

                    }

                },

                animation: {

                    duration: 1800,

                    easing: "easeOutQuart"

                }

            }

        });

    }


});
