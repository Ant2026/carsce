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

        const objetivo = parseInt(numero.textContent.replace(/,/g, ""));

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
        GRÁFICO
    =========================================*/

    const canvas = document.getElementById("grafico_dashboard");

    if (canvas) {

        new Chart(canvas, {

            type: "bar",

            data: {

                labels: [

                    "Enero",
                    "Febrero",
                    "Marzo",
                    "Abril",
                    "Mayo",
                    "Junio"

                ],

                datasets: [

                    {

                        label: "Estudiantes",

                        data: [

                            120,
                            190,
                            160,
                            240,
                            280,
                            330

                        ],

                        backgroundColor: [

                            "#2563EB",
                            "#2563EB",
                            "#2563EB",
                            "#2563EB",
                            "#2563EB",
                            "#2563EB"

                        ],

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