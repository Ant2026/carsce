flatpickr("#fecha_grado", {
    dateFormat: "Y-m-d",
    enable: [
        function(date) {
            return date.getDate() === 15 && date.getMonth() === 6;
        }
    ]
});