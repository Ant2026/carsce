function configurarFechaGrado(inputFecha, edadMinima) {
    const anio = new Date().getFullYear() - edadMinima;

    inputFecha.max = `${anio}-12-31`;
}