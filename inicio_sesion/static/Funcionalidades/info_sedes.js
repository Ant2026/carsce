document.addEventListener("DOMContentLoaded", () => {

    const contenedor_imagenes = document.getElementById("slides");
    let index = 0;
    
    const imagenes = [
        "static/Imagenes/sede_Barinas.png",
        "static/Imagenes/sede_Barinitas.png",
        "static/Imagenes/sede_Pedraza.png",
        "static/Imagenes/sede_Socopo.png"
    ];

    imagenes.forEach(ruta => {
        const img = document.createElement("img");
        img.src = ruta;
        contenedor_imagenes.appendChild(img);
    });

    function moverCarrusel() {
        contenedor_imagenes.style.transform = `translateX(-${index * 100}%)`;
    }
    
    setInterval(() => {
        index = (index + 1) % imagenes.length;
        moverCarrusel();
    }, 3000);

    const carreras_sedes = {
        'Barinas': {
            carreras: ["Ingeniería En Sistema e Infórmatica", "Ingeniería Electrónica", "Medicina Veterinaria", "Nutrición y Dietetica"],
            tipos_grados: ["TSU - Ingeniería", "TSU - Ingeniería", "Licenciatura", "Licenciatura"],
            duracion: ["4 años", "4 años", "5 años", "5 años"]
        },
        'Barinitas': {
            carreras: ["Ingeniería En Electricidad", "Ingeniería En Mecánica", "Ingeniería En AgroAlimentación", "Ingeniería En Construcción Civil", "Ingeniería Industrial", "Ingeniería En Sistema e Informática", "Medicina Veterinaria"],
            tipos_grados: ["TSU - Ingeniería", "TSU - Ingeniería", "TSU - Ingeniería", "TSU - Ingeniería", "TSU - Ingeniería", "TSU - Ingeniería", "Licenciatura"],
            duracion: ["4 años", "4 años", "4 años", "4 años", "4 años", "4 años", "5 años"]
        },
        'Socopo': {
            carreras: ["Ingeniería En Electricidad", "Ingeniería En AgroAlimentación", "Ingeniería En Construcción Civil", "Ingeniería En Sistema e Informática", "Medicina Veterinaria"],
            tipos_grados: ["TSU - Ingeniería", "TSU - Ingeniería", "TSU - Ingeniería", "TSU - Ingeniería", "Licenciatura"],
            duracion: ["4 años", "4 años", "4 años", "4 años", "5 años"]
        },
        'Pedraza': {
            carreras: ["Ingeniería En AgroAlimentación", "Medicina Veterinaria"],
            tipos_grados: ["TSU - Ingeniería", "Licenciatura"],
            duracion: ["4 años", "5 años"]
        }
    }

    const sedes = Object.keys(carreras_sedes);

    const contenedor = document.getElementById("contenedor_carrera");
    const titulo = document.getElementById("info_sedes");

    const btn_avanzar = document.getElementById("avanzar");
    const btn_retroceder = document.getElementById("retoceder");

    let sedeIndex = 0;

    function mostrar() {
        const sedeActual = sedes[sedeIndex];
        const data = carreras_sedes[sedeActual];

        titulo.textContent = `Carreras Impartidas en la sede ${sedeActual}`;

        contenedor.innerHTML = "";

        data.carreras.forEach((carrera, i) => {
            contenedor.innerHTML += `
                <tr>
                    <td>${carrera}</td>
                    <td>${data.tipos_grados[i]}</td>
                    <td>${data.duracion[i]}</td>
                </tr>
            `;
        });
    }

    mostrar();

    btn_avanzar.addEventListener("click", () => {
        if (sedeIndex < sedes.length - 1) {
            sedeIndex++;
            mostrar();
        }
    });

    btn_retroceder.addEventListener("click", () => {
        if (sedeIndex > 0) {
            sedeIndex--;
            mostrar();
        }
    });
});