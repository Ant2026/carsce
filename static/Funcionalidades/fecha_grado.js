function configurarFechaGrado(inputFecha, edadMinima) {
    const anio = new Date().getFullYear() - edadMinima;

    inputFecha.max = `${anio}-12-31`;

    inputFecha.addEventListener("keydown", e => e.preventDefault());
    inputFecha.addEventListener("paste", e => e.preventDefault());
}