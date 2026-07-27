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

});