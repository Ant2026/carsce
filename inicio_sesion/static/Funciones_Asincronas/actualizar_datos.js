document.addEventListener("DOMContentLoaded", () => {
    
    // Formulario
    const formulario_actualizar_usuario = document.getElementById("formulario_actualizar_usuario")
    const formulario_busqueda_usuario = document.getElementById("formulario_busqueda_usuario")

    const nacionalidad_busqueda = document.getElementById("nacionalidad_busqueda")
    const cedula_identidad_busqueda = document.getElementById("cedula_identidad_busqueda")

    // Básico
    const id_seleccionado = document.getElementById("id_seleccionado")
    const nombres_actualizar_usuario = document.getElementById("nombres_actualizar_usuario")
    const apellidos_actualizar_usuario = document.getElementById("apellidos_actualizar_usuario")
    const genero_actualizar_usuario = document.getElementById("genero_actualizar_usuario")
    const nacionalidad_actualizar_usuario = document.getElementById("nacionalidad_actualizar_usuario")
    const cedula_identidad_actualizar_usuario = document.getElementById("cedula_identidad_actualizar_usuario")
    const estado_civil_actualizar_usuario = document.getElementById("estado_civil_actualizar_usuario")
    
    // Contacto
    const prefijo_telefono_principal_actualizar = document.getElementById("prefijo_telefono_principal_actualizar")
    const num_telefono_principal_actualizar = document.getElementById("num_telefono_principal_actualizar")
    const prefijo_telefono_secundaria_actualizar = document.getElementById("prefijo_telefono_secundaria_actualizar")
    const num_telefonico_secundaria_actualizar = document.getElementById("num_telefonico_secundaria_actualizar")
    const correo_principal_actualizar = document.getElementById("correo_principal_actualizar")
    const dominio_principal_actualizar = document.getElementById("dominio_principal_actualizar")
    const correo_secundaria_actualizar = document.getElementById("correo_secundaria_actualizar")
    const dominio_secundaria_actualizar = document.getElementById("dominio_secundaria_actualizar")
    
    // Nacimiento
    const pais_nacimiento = document.getElementById("pais_nacimiento")
    
    const estado_nacimiento = document.getElementById("estado_nacimiento")
    const estado_novzla = document.getElementById("estado_novzla")
    
    const municipio_nacimiento = document.getElementById("municipio_nacimiento")
    const municipio_novzla = document.getElementById("municipio_novzla")
    
    const parroquia_nacimiento = document.getElementById("parroquia_nacimiento")
    const parroquia_novzla = document.getElementById("parroquia_novzla")
    
    const direccion_nacimiento = document.getElementById("direccion_nacimiento")
    const fecha_nacimiento = document.getElementById("fecha_nacimiento")
    
    // Residencia
    const condicion_residencia = document.getElementById("condicion_residencia")
    const municipio_residencia = document.getElementById("municipio_residencia")
    const parroquia_residencia = document.getElementById("parroquia_residencia")
    const direccion_domicilio = document.getElementById("direccion_domicilio")
    
    // Profesión
    const profesion_usuario = document.getElementById("profesion_usuario")
    const universidad_usuario = document.getElementById("universidad_usuario")
    const pais_profesion = document.getElementById("pais_profesion")

    // Secundaria
    const tipos_secundaria = document.getElementById("tipos_secundaria")
    const nombre_liceo = document.getElementById("nombre_liceo")
    const fecha_grado = document.getElementById("fecha_grado")
    const codigo_sin_opsu = document.getElementById("codigo_sin_opsu")
    
    // Representante
    const nombres_representante = document.getElementById("nombres_representante")
    const apellidos_representante = document.getElementById("apellidos_representante")
    const nacionalidad_representante = document.getElementById("nacionalidad_representante")
    const cedula_identidad_representante = document.getElementById("cedula_identidad_representante")
    const prefijo_telefono_representante = document.getElementById("prefijo_telefono_representante")
    const numero_telefono_representante = document.getElementById("numero_telefono_representante")
    const parestenco_representante = document.getElementById("parestenco_representante")
    
    const nombres_otrorepresentante = document.getElementById("nombres_otrorepresentante")
    const apellidos_otrorepresentante = document.getElementById("apellidos_otrorepresentante")
    const nacionalidad_otrorepresentante = document.getElementById("nacionalidad_otrorepresentante")
    const cedula_identidad_otrorepresentante = document.getElementById("cedula_identidad_otrorepresentante")
    const prefijo_telefono_otrorepresentante = document.getElementById("prefijo_telefono_otrorepresentante")
    const numero_telefono_otrorepresentante = document.getElementById("numero_telefono_otrorepresentante")
    const otroparestenco = document.getElementById("otroparestenco")

    // Discapacidad 
    const codigo_carnet_dispacidad = document.getElementById("codigo_carnet_dispacidad")
    const nro_registro_medico = document.getElementById("nro_registro_medico")
    const tipos_discapacidad = document.getElementById("tipos_discapacidad")
    const grado_discapacidad = document.getElementById("grado_discapacidad")
    const causa_discapacidad = document.getElementById("causa_discapacidad")

    const btn_discapacidad = document.getElementById("btn_discapacidad")
    const btn_otro_representante = document.getElementById("btn_otro_representante")
    const contenedor_otrorepresentante = document.getElementById("subcontenedor_representante")

    const bloqueProfesion = document.getElementById("datos_profesion");
    const bloqueSecundaria = document.getElementById("secundaria");
    const bloqueRepresentante = document.getElementById("representante");
    const bloqueDiscapacidad = document.getElementById("discapacidad");

    const prefijos = ["0414", "0424", "0416", "0426", "0412", "0422"];

    const parentescos = [
        "Padre",
        "Madre",
        "Abuelo",
        "Abuela",
        "Hermano",
        "Hermana",
        "Tío",
        "Tía",
        "Primo",
        "Prima",
        "Padrastro",
        "Madrastra",
        "Tutor legal",
        "Representante legal",
        "Cónyuge",
        "Otro"
    ];

    const paises = [
        "Afganistán",
        "Albania",
        "Alemania",
        "Andorra",
        "Angola",
        "Antigua y Barbuda",
        "Arabia Saudita",
        "Argelia",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaiyán",
        "Bahamas",
        "Bangladés",
        "Barbados",
        "Baréin",
        "Bélgica",
        "Belice",
        "Benín",
        "Bielorrusia",
        "Birmania",
        "Bolivia",
        "Bosnia y Herzegovina",
        "Botsuana",
        "Brasil",
        "Brunéi",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Bután",
        "Cabo Verde",
        "Camboya",
        "Camerún",
        "Canadá",
        "Catar",
        "Chad",
        "Chile",
        "China",
        "Chipre",
        "Ciudad del Vaticano",
        "Colombia",
        "Comoras",
        "Corea del Norte",
        "Corea del Sur",
        "Costa de Marfil",
        "Costa Rica",
        "Croacia",
        "Cuba",
        "Dinamarca",
        "Dominica",
        "Ecuador",
        "Egipto",
        "El Salvador",
        "Emiratos Árabes Unidos",
        "Eritrea",
        "Eslovaquia",
        "Eslovenia",
        "España",
        "Estados Unidos",
        "Estonia",
        "Etiopía",
        "Filipinas",
        "Finlandia",
        "Fiyi",
        "Francia",
        "Gabón",
        "Gambia",
        "Georgia",
        "Ghana",
        "Granada",
        "Grecia",
        "Guatemala",
        "Guyana",
        "Guinea",
        "Guinea ecuatorial",
        "Guinea-Bisáu",
        "Haití",
        "Honduras",
        "Hungría",
        "India",
        "Indonesia",
        "Irak",
        "Irán",
        "Irlanda",
        "Islandia",
        "Islas Marshall",
        "Islas Salomón",
        "Israel",
        "Italia",
        "Jamaica",
        "Japón",
        "Jordania",
        "Kazajistán",
        "Kenia",
        "Kirguistán",
        "Kiribati",
        "Kuwait",
        "Laos",
        "Lesoto",
        "Letonia",
        "Líbano",
        "Liberia",
        "Libia",
        "Liechtenstein",
        "Lituania",
        "Luxemburgo",
        "Madagascar",
        "Malasia",
        "Malaui",
        "Maldivas",
        "Malí",
        "Malta",
        "Marruecos",
        "Mauricio",
        "Mauritania",
        "México",
        "Micronesia",
        "Moldavia",
        "Mónaco",
        "Mongolia",
        "Montenegro",
        "Mozambique",
        "Namibia",
        "Nauru",
        "Nepal",
        "Nicaragua",
        "Níger",
        "Nigeria",
        "Noruega",
        "Nueva Zelanda",
        "Omán",
        "Países Bajos",
        "Pakistán",
        "Palaos",
        "Panamá",
        "Papúa Nueva Guinea",
        "Paraguay",
        "Perú",
        "Polonia",
        "Portugal",
        "Reino Unido",
        "República Centroafricana",
        "República Checa",
        "República de Macedonia",
        "República del Congo",
        "República Democrática del Congo",
        "República Dominicana",
        "República Sudafricana",
        "Ruanda",
        "Rumanía",
        "Rusia",
        "Samoa",
        "San Cristóbal y Nieves",
        "San Marino",
        "San Vicente y las Granadinas",
        "Santa Lucía",
        "Santo Tomé y Príncipe",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leona",
        "Singapur",
        "Siria",
        "Somalia",
        "Sri Lanka",
        "Suazilandia",
        "Sudán",
        "Sudán del Sur",
        "Suecia",
        "Suiza",
        "Surinam",
        "Tailandia",
        "Tanzania",
        "Tayikistán",
        "Timor Oriental",
        "Togo",
        "Tonga",
        "Trinidad y Tobago",
        "Túnez",
        "Turkmenistán",
        "Turquía",
        "Tuvalu",
        "Ucrania",
        "Uganda",
        "Uruguay",
        "Uzbekistán",
        "Vanuatu",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Yibuti",
        "Zambia",
        "Zimbabue"
    ];

    const Estado = [
        "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", "Carabobo", "Cojedes",
        "Delta Amacuro", "Distrito Capital", "Falcón", "Guárico", "Lara", "Mérida", "Miranda", "Monagas",
        "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo", "La Guaira", "Yaracuy", "Zulia", "Dependencias"
    ];

    const municipiosPorEstado = {
        "Amazonas": [
            "Alto Orinoco", "Atabapo", "Atures", "Autana", "Maroa", "Manapiare", "Río Negro"
        ],
        "Anzoátegui": [
            "Anaco", "Aragua", "Bolívar", "Bruzual", "Cajigal", "Carvajal", "Diego Bautista Urbaneja",
            "Freites", "Guanipa", "Guanta", "Independencia", "Libertad", "McGregor", "Miranda",
            "Monagas", "Peñalver", "Píritu", "San Juan de Capistrano", "Santa Ana", "Simón Rodríguez", "Sotillo"
        ],
        "Apure": [
            "Achaguas", "Biruaca", "Muñoz", "Páez", "Pedro Camejo", "Rómulo Gallegos", "San Fernando"
        ],
        "Aragua": [
            "Bolívar", "Camatagua", "Francisco Linares Alcántara", "Girardot", "José Ángel Lamas",
            "José Félix Ribas", "José Rafael Revenga", "Libertador", "Mario Briceño Iragorry",
            "Ocumare de la Costa de Oro", "San Casimiro", "San Sebastián", "Santiago Mariño",
            "Santos Michelena", "Sucre", "Tovar", "Urdaneta", "Zamora"
        ],
        "Barinas": [
            "Alberto Arvelo Torrealba", "Andrés Eloy Blanco", "Antonio José de Sucre", "Arismendi",
            "Barinas", "Bolívar", "Cruz Paredes", "Ezequiel Zamora", "Obispos", "Pedraza",
            "Rojas", "Sosa"
        ],
        "Bolívar": [
            "Caroní", "Cedeño", "El Callao", "Gran Sabana", "Heres", "Piar", "Raúl Leoni",
            "Roscio", "Sifontes", "Sucre", "Padre Pedro Chien"
        ],
        "Carabobo": [
            "Bejuma", "Carlos Arvelo", "Diego Ibarra", "Guacara", "Juan José Mora", "Libertador",
            "Los Guayos", "Miranda", "Montalbán", "Naguanagua", "Puerto Cabello", "San Diego", "San Joaquín", "Valencia"
        ],
        "Cojedes": [
            "Anzoátegui", "El Pao", "Falcón", "Girardot", "Lima Blanco", "Pao de San Juan Bautista",
            "Ricaurte", "Rómulo Gallegos", "San Carlos", "Tinaco"
        ],
        "Delta Amacuro": [
            "Antonio Díaz", "Casacoima", "Pedernales", "Tucupita"
        ],
        "Distrito Capital": [
            "Libertador"
        ],
        "Falcón": [
            "Acosta", "Bolívar", "Buchivacoa", "Cacique Manaure", "Carirubana", "Colina", "Dabajuro",
            "Democracia", "Falcón", "Federación", "Jacura", "Los Taques", "Mauroa", "Miranda",
            "Monseñor Iturriza", "Palmasola", "Petit", "Píritu", "San Francisco", "Silva",
            "Sucre", "Tocópero", "Unión", "Urumaco", "Zamora"
        ],
        "Guárico": [
            "Camaguán", "Chaguaramas", "El Socorro", "Francisco de Miranda", "José Félix Ribas",
            "José Tadeo Monagas", "Juan Germán Roscio", "Julián Mellado", "Las Mercedes", "Leonardo Infante",
            "Ortiz", "San Gerónimo de Guayabal", "San José de Guaribe", "Santa María de Ipire"
        ],
        "La Guaira": [
            "Vargas"
        ],
        "Lara": [
            "Andrés Eloy Blanco", "Crespo", "Iribarren", "Jiménez", "Morán", "Palavecino",
            "Simón Planas", "Torres", "Urdaneta"
        ],
        "Mérida": [
            "Alberto Adriani", "Andrés Bello", "Antonio Pinto Salinas", "Aricagua", "Arzobispo Chacón",
            "Campo Elías", "Caracciolo Parra Olmedo", "Cardenal Quintero", "Guaraque", "Julio César Salas",
            "Justo Briceño", "Libertador", "Miranda", "Obispo Ramos de Lora", "Padre Noguera", "Pueblo Llano",
            "Rangel", "Rivas Dávila", "Santos Marquina", "Sucre", "Tovar", "Tulio Febres Cordero", "Zea"
        ],
        "Miranda": [
            "Acevedo", "Andrés Bello", "Baruta", "Brión", "Buroz", "Carrizal", "Chacao", "Cristóbal Rojas",
            "El Hatillo", "Guaicaipuro", "Independencia", "Lander", "Los Salias", "Páez", "Paz Castillo",
            "Pedro Gual", "Plaza", "Simón Bolívar", "Sucre", "Urdaneta", "Zamora"
        ],
        "Monagas": [
            "Acosta", "Aguasay", "Bolívar", "Caripe", "Cedeño", "Ezequiel Zamora", "Libertador",
            "Maturín", "Piar", "Punceres", "Santa Bárbara", "Sotillo", "Uracoa"
        ],
        "Nueva Esparta": [
            "Antolín del Campo", "Arismendi", "Díaz", "García", "Gómez", "Maneiro", "Marcano",
            "Mariño", "Península de Macanao", "Tubores", "Villalba"
        ],
        "Portuguesa": [
            "Agua Blanca", "Araure", "Esteller", "Guanare", "Guanarito", "Monseñor José Vicente de Unda",
            "Ospino", "Páez", "Papelón", "San Genaro de Boconoito", "San Rafael de Onoto", "Santa Rosalía",
            "Sucre", "Turén"
        ],
        "Sucre": [
            "Andrés Eloy Blanco", "Andrés Mata", "Arismendi", "Benítez", "Bermúdez", "Bolívar",
            "Cajigal", "Cruz Salmerón Acosta", "Libertador", "Mariño", "Mejía", "Montes", "Ribero", "Sucre", "Valdez"
        ],
        "Táchira": [
            "Andrés Bello", "Antonio Rómulo Costa", "Ayacucho", "Bolívar", "Cárdenas", "Córdoba", "Fernández Feo",
            "Francisco de Miranda", "García de Hevia", "Guásimos", "Independencia", "Jáuregui", "José María Vargas",
            "Junín", "Libertad", "Libertador", "Lobatera", "Michelena", "Panamericano", "Pedro María Ureña",
            "Rafael Urdaneta", "Samuel Darío Maldonado", "San Cristóbal", "Seboruco", "Simón Rodríguez", "Sucre", "Torbes", "Uribante"
        ],
        "Trujillo": [
            "Andrés Bello", "Boconó", "Bolívar", "Candelaria", "Carache", "Escuque", "José Felipe Márquez Cañizales",
            "Juan Vicente Campos Elías", "La Ceiba", "Miranda", "Monte Carmelo", "Motatán", "Pampán",
            "Pampanito", "Rafael Rangel", "San Rafael de Carvajal", "Sucre", "Trujillo", "Urdaneta", "Valera"
        ],
        "Yaracuy": [
            "Arístides Bastidas", "Bolívar", "Bruzual", "Cocorote", "Independencia", "José Antonio Páez",
            "La Trinidad", "Manuel Monge", "Nirgua", "Peña", "San Felipe", "Sucre", "Urachiche", "Veroes"
        ],
        "Zulia": [
            "Almirante Padilla", "Baralt", "Cabimas", "Catatumbo", "Colón", "Francisco Javier Pulgar",
            "Guajira", "Jesús Enrique Lossada", "Jesús María Semprún", "La Cañada de Urdaneta", "Lagunillas",
            "Machiques de Perijá", "Mara", "Maracaibo", "Miranda", "Rosario de Perijá", "San Francisco",
            "Santa Rita", "Simón Bolívar", "Sucre", "Valmore Rodríguez"
        ]
    };

    const parroquiasPorMunicipio = {
        "Amazonas": {
            "Alto Orinoco": ["La Esmeralda", "Huachamacare", "Marawaka", "Mavaca", "Sierra Parima"],
            "Atabapo": ["San Fernando de Atabapo", "Ucata", "Yapacana", "Caname"],
            "Atures": ["Fernando Girón Tovar", "Luis Alberto Gómez", "Parhueña", "Platanillal"],
            "Autana": ["Isla de Ratón", "Samariapo", "Sipapo", "Munduapo", "Guayapo"],
            "Maroa": ["Maroa", "Comunidad", "Victorino"],
            "Manapiare": ["San Juan de Manapiare", "Alto Ventuari", "Medio Ventuari", "Bajo Ventuari"],
            "Río Negro": ["San Carlos de Río Negro", "Solano", "Casiquiare", "Cocuy"]
        },
        "Anzoátegui": {
            "Anaco": ["Anaco", "San Joaquín"],
            "Aragua": ["Aragua de Barcelona", "Cachipo"],
            "Fernando de Peñalver": ["Puerto Píritu", "San Miguel", "Sucre"],
            "Francisco del Carmen Carvajal": ["Valle de Guanape", "Santa Bárbara"],
            "Francisco de Miranda": ["Pariaguán"],
            "Guanta": ["Guanta", "Chorrerón"],
            "Independencia": ["Soledad"],
            "José Gregorio Monagas": ["Mapire", "Piar", "Santa Clara", "San Diego de Cabrutica", "Uverito", "Zuata"],
            "Juan Antonio Sotillo": ["Puerto La Cruz"],
            "Juan Manuel Cajigal": ["Onoto", "San Pablo"],
            "Libertad": ["San Mateo", "El Carito", "Santa Inés"],
            "Manuel Ezequiel Bruzual": ["Clarines", "Guanape", "Sabana de Uchire"],
            "Pedro María Freites": ["Cantaura", "Libertador", "Santa Rosa", "Urica"],
            "Píritu": ["Píritu", "San Francisco"],
            "San José de Guanipa": ["San José de Guanipa"],
            "San Juan de Capistrano": ["Boca de Uchire", "Boca de Chávez"],
            "Santa Ana": ["Santa Ana", "Boca de Santa Ana"],
            "Simón Bolívar": ["Bergantín", "Caigua", "El Carmen", "El Pilar", "Naricual", "San Cristóbal"],
            "Simón Rodríguez": ["El Tigre"]
        },
        "Apure": {
            "Achaguas": ["Achaguas", "Apurito", "El Yagual", "Guachara", "Mucuritas", "Queseras del Medio"],
            "Biruaca": ["Biruaca"],
            "Muñoz": ["Bruzual", "Mantecal", "Quintero", "Rincón Hondo", "San Vicente"],
            "Páez": ["Guasdualito", "Aramendi", "El Amparo", "San Camilo", "Urdaneta"],
            "Pedro Camejo": ["San Juan de Payara", "Codazzi", "Cunaviche"],
            "Rómulo Gallegos": ["Elorza", "La Trinidad"],
            "San Fernando": ["San Fernando", "El Recreo", "Peñalver", "San Rafael de Atamaica"]
        },
        "Aragua": {
            "Bolívar": ["San Mateo"],
            "Camatagua": ["Camatagua", "Carmen de Cura"],
            "Francisco Linares Alcántara": ["Santa Rita", "Francisco de Miranda", "Monseñor Feliciano González"],
            "Girardot": ["Pedro José Ovalles", "Joaquín Crespo", "José Casanova Godoy", "Madre María de San José", "Andrés Eloy Blanco", "Los Tacarigua", "Las Delicias", "Choroní"],
            "José Ángel Lamas": ["Santa Cruz"],
            "José Félix Ribas": ["Victoria", "Zuata", "La Quebrada", "Pao de Zárate", "Castor Nieves Ríos"],
            "José Rafael Revenga": ["El Consejo"],
            "Libertador": ["Palo Negro", "San Martín de Porres"],
            "Mario Briceño Iragorry": ["El Limón", "Caña de Azúcar"],
            "Ocumare de la Costa de Oro": ["Ocumare de la Costa"],
            "San Casimiro": ["San Casimiro", "Güiripa", "Ollas de Caramacate", "Valle Morín"],
            "San Sebastián": ["San Sebastián"],
            "Santiago Mariño": ["Turmero", "Arévalo Aponte", "Chuao", "Samán de Güere", "Alfredo Pacheco Miranda"],
            "Santos Michelena": ["Las Tejerías", "Tiara"],
            "Sucre": ["Cagua", "Bella Vista"],
            "Tovar": ["Colonia Tovar"],
            "Urdaneta": ["Barbacoas", "Las Peñitas", "San Francisco de Cara", "Taguay"],
            "Zamora": ["Villa de Cura", "Magdaleno", "San Francisco de Asís", "Valles de Tucutunemo", "Augusto Mijares"]
        },
        "Trujillo": {
            "Andrés Bello": ["Santa Isabel", "Araguaney", "El Jaguito", "La Esperanza"],
            "Boconó": ["Boconó", "Ayacucho", "Burbusay", "El Carmen", "General Ribas", "Guaramacal", "Monseñor Jáuregui", "Mosquey", "Rafael Rangel", "San José", "San Miguel", "Vega de Guaramacal"],
            "Bolívar": ["Sabana Grande", "Cheregüé", "Granados"],
            "Candelaria": ["Chejendé", "Arnoldo Gabaldón", "Bolivia", "Carrillo", "Cegarra", "Manuel Salvador Ulloa", "San José"],
            "Carache": ["Carache", "Cuicas", "La Concepción", "Panamericana", "Santa Cruz"],
            "Escuque": ["Escuque", "La Unión", "Sabana Libre", "Santa Rita"],
            "José Felipe Márquez Cañizales": ["El Socorro", "Antonio José de Sucre", "Los Caprichos"],
            "Juan Vicente Campo Elías": ["Campo Elia", "La Placita", "Los Caprichos"],
            "La Ceiba": ["Santa Apolonia", "Zona Rica", "La Ceiba"],
            "Miranda": ["El Dividive", "Agua Santa", "Agua Caliente", "El Cenizo", "Valerita"],
            "Monte Carmelo": ["Monte Carmelo", "Buena Vista", "Casa de Tabla"],
            "Motatán": ["Motatán", "El Baño", "Jalisco"],
            "Pampán": ["Pampán", "Flor de Patria", "Monay", "Santa Ana"],
            "Pampanito": ["Pampanito", "La concepción", "Pampanito II"],
            "parroquias": ["Betijoque", "José Gregorio Hernández", "La Pueblita", "Los Cedros"],
            "San Rafael de Carvajal": ["Carvajal", "La Cejita", "Campo Alegre", "Las Mesetas"],
            "Sucre": ["Sabana de Mendoza", "El Paraiso", "Junín", "Valmore Rodríguez"],
            "Trujillo": ["Trujillo", "San Lázaro", "Chiquinquirá", "Santa Rosa", "La Plazuela", "San Jacinto", "Tres Esquinas"],
            "Urdaneta": ["Cabimbú", "Jajó", "La Mesa de Esnujaque", "Santiago", "Tuñame", "La Quebrada"],
            "Valera": ["Juan Ignacio Montilla", "La Beatriz", "La Puerta", "Mendoza", "Mercedes Díaz", "San Luis"]
        },
        "Barinas": {
            "Alberto Arvelo Torrealba": ["Sabaneta", "Rodríguez Domínguez"],
            "Andrés Eloy Blanco": ["El Cantón", "Santa Cruz de Guacas", "Puerto Vivas"],
            "Antonio José de Sucre": ["Socopó"],
            "Arismendi": ["Arismendi", "Guadarrama", "La Unión", "San Antonio"],
            "Barinas": ["Alto Barinas", "Alberto Arvelo Larriva", "San Silvestre", "Santa Inés", "Santa Lucía", "Torunos", "El Carmen", "Rómulo Betancourt", "Corazón de Jesús", "Ramón Ignacio Méndez", "Manuel Palacio Fajardo", "Juan Antonio Rodríguez Domínguez", "Domingo Ortiz de Páez"],
            "Bolívar": ["Barinitas", "Altamira de Cáceres", "Calderas"],
            "Cruz Paredes": ["Barrancas", "El Socorro", "Masparrito"],
            "Ezequiel Zamora": ["Santa Bárbara", "José Ignacio del Pumar", "Pedro Briceño Méndez", "Ramón Ignacio Méndez"],
            "Obispo": ["Obispos", "El Real", "La Luz", "Los Guasimitos"],
            "Pedraza": ["Ciudad Bolivia", "Ignacio Briceño", "José Félix Ribas", "Páez"],
            "Rojas": ["Libertad", "Dolores", "Palacios Fajardo", "Santa Rosa", "Simón Rodríguez"],
            "Sosa": ["Ciudad de Nutrias", "El Regalo", "Puerto de Nutrias", "Santa Catalina", "Simón Bolívar"]
        },
        "Bolívar": {
            "Caroní": ["Ciudad Guayana", "Parroquia Cachamay", "Parroquia Chirica", "Parroquia Dalla Costa", "Parroquia Simón Bolívar", "Parroquia Unare"],
            "Cedeño": ["Caicara del Orinoco", "Altagracia", "Ascensión Farreras", "Guaniamo", "La Urbana"],
            "Gran Sabana": ["Ikabarú", "Kavanayén", "Santa Elena de Uairén"],
            "Heres": ["Ciudad Bolívar", "Catedral", "Simón Bolívar", "Marhuanta"],
            "Piar": ["Aripao", "El Pao", "Upata", "San Félix", "El Manteco", "Tumeremo"],
            "Roscio": ["Guasipati", "El Callao"],
            "Sifontes": ["El Dorado", "Tumeremo", "San Isidro"],
            "Sucre": ["Maripa", "Barbacoa", "El Pao"]
        },
        "Carabobo": {
            "Bejuma": ["Bejuma", "Canoabo", "Simón Bolívar", "Fraternidad", "José Rafael Pulgar"],
            "Carlos Arvelo": ["Güigüe", "Tocuyito", "Unión", "Miranda", "Independencia", "Puerto Cabello"],
            "Juan José Mora": ["Morón", "Guacara", "Begoña", "Yagua", "Tacarigua"],
            "Libertador": ["Naguanagua", "San Joaquín", "Morón", "Valencia"],
            "Los Guayos": ["Los Guayos", "Catedral", "Guacara", "Tocuyito"],
            "Puerto Cabello": ["Puerto Cabello", "Bartolomé Salom", "Unión", "Borburata", "Juan José Flores"],
            "San Diego": ["San Diego", "Dallago", "Cascabel", "Vigirima"],
            "San Joaquín": ["San Joaquín", "El Pao", "Quirindai", "Nicolas Pulido"]
        },
        "Cojedes": {
            "Anzoátegui": ["Macapo", "El Baúl", "Puerto Colorado"],
            "Cojedes": ["San Carlos", "Juan de Mata Suárez", "Ramón Ignacio Méndez", "Libertad", "El Pao", "Evaristo Fernández"],
            "Ricaurte": ["Libertad", "El Amparo", "La Aguadita", "Monte Verde"],
            "Pao de San Juan Bautista": ["Pao", "El Baúl", "Las Vegas", "Santa Apolonia"],
            "Tinaco": ["Tinaco", "San Carlos", "Sucre", "Santa Inés"]
        },
        "Delta Amacuro": {
            "Antonio Díaz": ["Antonio Díaz", "Boca de Uracoa", "Boca de Tucupita"],
            "Casacoima": ["Casacoima", "Pedernales", "Tucupita", "El Triunfo"],
            "Tucupita": ["San José de Tucupita", "Boca de Manamo", "Curiapo", "Parguaza"]
        },
        "Falcón": {
            "Buchivacoa": ["Churuguara", "Las Calderas", "Caujaro", "Pueblo Nuevo"],
            "Carirubana": ["Punto Fijo", "Judibana", "Santa Ana"],
            "Colina": ["Chichiriviche", "La Vela de Coro", "Capanaparo", "Cumarebo"],
            "Dabajuro": ["Dabajuro", "Mene de Mauroa"],
            "Falcón": ["Coro", "Santa Ana", "Tocuyo de la Costa", "San Luis"],
            "José Laurencio Silva": ["Judibana", "Santa Ana", "Pueblo Nuevo"],
            "Los Taques": ["Los Taques", "Judibana", "Santa Cruz de Los Taques"],
            "Mauroa": ["Mauroa", "Mene de Mauroa"],
            "Miranda": ["Miranda", "Pueblo Nuevo", "La Vela de Coro"],
            "Monseñor Iturriza": ["Monseñor Iturriza", "Judibana", "Santa Ana"]
        },
        "Guárico": {
            "Camaguán": ["Camaguán", "Uverito", "Chaguaramas"],
            "Chaguaramas": ["Chaguaramas", "El Socorro", "Las Mercedes del Llano"],
            "El Socorro": ["El Socorro", "Las Mercedes del Llano", "San Juan de los Morros"],
            "José Félix Ribas": ["Ortiz", "Tucupido", "Altagracia de Orituco"],
            "Juan Germán Roscio": ["Calabozo", "Las Mercedes", "El Sombrero"],
            "Las Mercedes": ["Las Mercedes", "Ortiz", "Valle de la Pascua"],
            "Leonardo Infante": ["El Sombrero", "Ortiz"],
            "Pedro Zaraza": ["Zaraza", "San José de Unare", "Ortiz"],
            "San Gerónimo de Guayabal": ["San Gerónimo de Guayabal"],
            "Valle de la Pascua": ["Valle de la Pascua", "Calabozo", "San Juan de Los Morros"]
        },
        "Lara": {
            "Iribarren": ["Barquisimeto", "Juan de Villegas", "Santa Rosa", "Atarigua", "Guacara"],
            "Morán": ["El Tocuyo", "Cubiro", "Duaca", "La Aguadita"],
            "Palavecino": ["Cabudare", "Judibana", "Moroturo"],
            "Simón Planas": ["Sarare", "Buría", "Guanare"],
            "Torres": ["Carora", "Aguada Grande", "Bobare"]
        },
        "Mérida": {
            "Alberto Adriani": ["Ejido", "La Azulita", "Lagunillas", "Mucuchíes", "Mucujepe"],
            "Andrés Bello": ["La Pedrera", "Santa Elena de Arenales"],
            "Antonio Pinto Salinas": ["Mérida", "Santa Cruz de Mora"],
            "Aricagua": ["Aricagua", "Chachopo"],
            "Arzobispo Chacón": ["Canagua", "Chiguará", "San Juan"],
            "Campo Elías": ["Ejido", "El Vigía", "Jají"],
            "Caracciolo Parra Olmedo": ["Tabay", "Timotes", "Tucaní"]
        },
        "Miranda": {
            "Acevedo": ["Petare", "Guarenas", "Guatire"],
            "Baruta": ["Baruta", "El Cafetal"],
            "Brión": ["Mamporal", "Curiepe"],
            "Carrizal": ["Carrizal", "Paracotos"],
            "Chacao": ["Chacao", "El Rosal"],
            "Cristóbal Rojas": ["Charallave", "Cúa"],
            "El Hatillo": ["El Hatillo", "La Lagunita"],
            "Los Salias": ["San Antonio de Los Altos", "Carrizal"],
            "Sucre": ["Petare", "Petare Central"],
            "Tomás Lander": ["Ocumare del Tuy", "Santa Teresa del Tuy"]
        },
        "Monagas": {
            "Acosta": ["San Antonio", "Quiriquire"],
            "Aguasay": ["Aguasay", "Jusepín"],
            "Ezequiel Zamora": ["Punta de Mata", "Temblador"],
            "Libertador": ["Temblador", "Temblador"],
            "Maturín": ["Maturín", "San Simón"],
            "Piar": ["Aragua de Maturín", "El Furrial"],
            "Santa Bárbara": ["Santa Bárbara", "Punta de Mata"],
            "Uracoa": ["Uracoa", "Barrancas"]
        },
        "Nueva Esparta": {
            "Antolín del Campo": ["La Plaza de Paraguachí", "Villa Rosa"],
            "Arismendi": ["La Asunción", "El Cercado"],
            "García": ["Porlamar", "Pampatar"],
            "Maneiro": ["Punta de Piedras", "El Valle del Espíritu Santo"],
            "Mariño": ["Porlamar", "Pampatar"]
        },
        "Portuguesa": {
            "Agua Blanca": ["Agua Blanca", "Los Cedros"],
            "Araure": ["Araure", "Ospino"],
            "Esteller": ["Biscucuy", "Guanare"],
            "Guanare": ["Guanare", "Biscucuy"],
            "Ospino": ["Ospino", "Píritu"],
            "Papelón": ["Papelón", "Mesa de Cavaca"],
            "San Genaro de Boconoíto": ["Boconoíto", "Mesa de Cavaca"],
            "Guanarito": ["Guanarito", "Trinidad de la Capilla", "Divina Pastora"]
        },
        "Sucre": {
            "Andrés Mata": ["Cumaná", "Guaraguao"],
            "Benítez": ["Carúpano", "El Pilar"],
            "Bermúdez": ["Cumanacoa", "Boca de Uchire"],
            "Bolívar": ["Santa Fe", "San Antonio"],
            "Cajigal": ["Río Caribe", "Catuaro"],
            "Libertador": ["Tunapuy", "Cariaco"],
            "Maturín": ["El Furrial", "San Antonio de Maturín"],
            "Ribero": ["Cariaco", "San José de Aerocuar"],
            "Valdez": ["Cumanacoa", "Marigüitar"]
        },
        "Distrito Capital": {
            "Libertador": [
                "23 de Enero", "Altagracia", "Catedral", "Coche", "El Paraíso",
                "El Recreo", "El Valle", "La Pastora", "La Vega", "Macarao",
                "San Agustín", "San Bernardino", "San José", "San Juan",
                "Santa Rosalía", "Santa Teresa"
            ]
        },
        "La Guaira": {
            "Vargas": [
                "Carayaca", "Caraballeda", "Catia La Mar", "El Junko",
                "La Guaira", "Macuto", "Naiguatá", "Caribe", "Maiquetía"
            ]
        },
        "Zulia": {
            "Almirante Padilla": [
                "Isla de Toas", "Monagas"
            ],
            "Baralt": [
                "San Timoteo", "General Urdaneta", "Libertador",
                "Marcelino Briceño", "Pueblo Nuevo", "Manuel Guanipa Matos"
            ],
            "Cabimas": [
                "Ambrosio", "Arístides Calvani", "Carmen Herrera",
                "Germán Ríos Linares", "Jorge Hernández", "La Rosa",
                "Punta Gorda", "Rómulo Betancourt", "San Benito"
            ],
            "Catatumbo": [
                "Encontrados", "Udón Pérez"
            ],
            "Colón": [
                "San Carlos del Zulia", "Moralito", "Santa Bárbara",
                "Santa Cruz del Zulia", "Urribarrí"
            ],
            "Francisco Javier Pulgar": [
                "Simón Rodríguez", "Agustín Codazzi",
                "Carlos Quevedo", "Francisco Javier Pulgar"
            ],
            "Guajira": [
                "Sinamaica", "Alta Guajira",
                "Elías Sánchez Rubio", "Guajira"
            ],
            "Jesús Enrique Lossada": [
                "La Concepción", "San José",
                "Mariano Parra León", "José Ramón Yépez"
            ],
            "Jesús María Semprún": [
                "Jesús María Semprún", "Barí"
            ],
            "La Cañada de Urdaneta": [
                "Concepción", "Andrés Bello",
                "Chiquinquirá", "El Carmelo", "Potreritos"
            ],
            "Lagunillas": [
                "Libertad", "Alonso de Ojeda",
                "Venezuela", "Eleazar López Contreras", "Campo Lara"
            ],
            "Machiques de Perijá": [
                "Bartolomé de las Casas", "Libertad",
                "Río Negro", "San José de Perijá"
            ],
            "Mara": [
                "San Rafael", "La Sierrita", "Las Parcelas",
                "Luis de Vicente", "Monseñor Marcos Sergio Godoy",
                "Ricaurte", "Tamare"
            ],
            "Maracaibo": [
                "Antonio Borjas Romero", "Bolívar", "Cacique Mara",
                "Carracciolo Parra Pérez", "Cecilio Acosta", "Cristo de Aranza",
                "Coquivacoa", "Chiquinquirá", "Francisco Eugenio Bustamante",
                "Idelfonso Vásquez", "Juana de Ávila", "Luis Hurtado Higuera",
                "Manuel Dagnino", "Olegario Villalobos", "Raúl Leoni",
                "Santa Lucía", "San Isidro", "Venancio Pulgar"
            ],
            "Miranda": [
                "Altagracia", "Faría", "Ana María Campos",
                "San Antonio", "San José"
            ],
            "Rosario de Perijá": [
                "Donaldo García", "El Rosario", "Sixto Zambrano"
            ],
            "San Francisco": [
                "San Francisco", "El Bajo", "Domitila Flores",
                "Francisco Ochoa", "Los Cortijos", "Marcial Hernández",
                "José Domingo Rus"
            ],
            "Santa Rita": [
                "Santa Rita", "El Mene", "Pedro Lucas Urribarrí",
                "José Cenobio Urribarrí"
            ],
            "Simón Bolívar": [
                "Rafael María Baralt", "Manuel Manrique", "Rafael Urdaneta"
            ],
            "Sucre": [
                "Bobures", "Gibraltar", "Heras",
                "Monseñor Arturo Álvarez", "Rómulo Gallegos", "El Batey"
            ],
            "Valmore Rodríguez": [
                "Rafael Urdaneta", "La Victoria", "Raúl Cuenca"
            ]
        }
    };

    const Paises_laborales = [
        "Venezuela", "Colombia", "Perú ", "Ecuador ", "Chile ", "Brasil ", "Panamá ", "República Dominicana",
        "Argentina ", "México ", "Estados Unidos", "Canadá ", "España ", "Italia", "Portugal ",
        "Francia", "Alemania", "Reino Unido"
    ];

    const municipios = [
        "Barinas", "Pedraza", "Antonio José de Sucre", "Ezequiel Zamora", "Bolívar", "Alberto Arvelo Torrealba", "Rojas", "Obispo", "Sosa", "Cruz Paredes", "Arismendi", "Andrés Eloy Blanco"
    ];

    const parroquiasPorMunicipios = {
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

    // validación para la cedula de identidad
    function longitud_identidad(select_nacionalidad, campo_cedula) {
        function actualizar() {
            const nacionalidad = select_nacionalidad.value;

            campo_cedula.value = "";

            if (nacionalidad === "") {
                campo_cedula.disabled = true;
                campo_cedula.placeholder = "Seleccione nacionalidad";
                return;
            }
            campo_cedula.disabled = false;

            switch (nacionalidad) {
                case "V":
                    campo_cedula.maxLength = 8;
                    campo_cedula.minLength = 7;
                    campo_cedula.placeholder = "Cédula de Identidad (7-8)";
                    break;
                case "E":
                    campo_cedula.maxLength = 10;
                    campo_cedula.minLength = 8;
                    campo_cedula.placeholder = "Pasaporte/DNI (8-10)";
                    break;
            }
        }

        campo_cedula.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "");
        });
        select_nacionalidad.addEventListener("change", actualizar);

        actualizar();
    }

    // Validación Correo
    function ValidarCorreo(input_correo, select_dominio_correo) {

        input_correo.addEventListener("keydown", function (e) {

            const caracter = e.key;

            const caracteres_denegados = [
                " ", "(", ")", "[", "]", "{", "}", "<", ">", ",", ";", ":",
                "\\", "/", "'", "\"", "|", "°", "¬", "¿", "?", "¡", "!",
                "#", "$", "%", "^", "&", "*", "=", "+", "~", "`", "-"
            ];

            if (caracteres_denegados.includes(caracter)) {
                e.preventDefault();
                return;
            }

            if (caracter === "." && this.value.includes(".")) {
                e.preventDefault();
                return;
            }

            if (caracter === "." && this.value.length === 0) {
                e.preventDefault();
                return;
            }

        });

        input_correo.addEventListener("input", function () {
            this.value = this.value
                .toLowerCase()
                .replace(/[^a-z0-9._]/g, "");
        });

        input_correo.addEventListener("paste", function (e) {
            e.preventDefault();
        });

        function DominioSelect() {

            const dominios = [
                "@gmail.com",
                "@outlook.com",
                "@yahoo.com"
            ];

            select_dominio_correo.innerHTML =
                "<option disabled selected hidden>DOMINIO</option>";

            input_correo.placeholder = "Nombre del correo electrónico";

            dominios.forEach(dominio => {
                const option = document.createElement("option");
                option.value = dominio;
                option.textContent = dominio;
                select_dominio_correo.appendChild(option);
            });
        }
        DominioSelect();
    }

    // validación de Telefono
    function ValidarTelefono(select_prefijo_telefonico, input_numerico_telefonico) {

        function prefijos_select() {

            select_prefijo_telefonico.innerHTML = "<option selected>TLF</option>";

            input_numerico_telefonico.placeholder =
                "Número telefónico debe llevar 7 dígitos";

            prefijos.forEach(prefijo => {
                const option = document.createElement("option");
                option.value = prefijo;
                option.textContent = prefijo;
                select_prefijo_telefonico.appendChild(option);
            });
        }

        prefijos_select();

        select_prefijo_telefonico.addEventListener("change", function () {
            input_numerico_telefonico.value = "";
            input_numerico_telefonico.disabled = false;
        });

        input_numerico_telefonico.addEventListener("keydown", function (e) {
            const caracter = e.key;

            const teclas_permitidas = [
                "Backspace",
                "ArrowLeft",
                "ArrowRight",
                "Delete",
                "Tab"
            ];

            if (teclas_permitidas.includes(caracter)) return;

            if (!/^\d$/.test(caracter)) {
                e.preventDefault();
                return;
            }

            if (this.value.length >= 7) {
                e.preventDefault();
            }
        });

        input_numerico_telefonico.addEventListener("paste", function (e) {
            e.preventDefault();
        });
    }

    longitud_identidad(nacionalidad_busqueda, cedula_identidad_busqueda);
    longitud_identidad(nacionalidad_actualizar_usuario, cedula_identidad_actualizar_usuario);
    longitud_identidad(nacionalidad_representante, cedula_identidad_representante);
    longitud_identidad(nacionalidad_otrorepresentante, cedula_identidad_otrorepresentante);

    ValidarCorreo(correo_principal_actualizar, dominio_principal_actualizar);
    ValidarCorreo(correo_secundaria_actualizar, dominio_secundaria_actualizar);

    ValidarTelefono(prefijo_telefono_principal_actualizar, num_telefono_principal_actualizar);
    ValidarTelefono(prefijo_telefono_secundaria_actualizar, num_telefonico_secundaria_actualizar);
    ValidarTelefono(prefijo_telefono_representante, numero_telefono_representante);
    ValidarTelefono(prefijo_telefono_otrorepresentante, numero_telefono_otrorepresentante);

    function parentesco_controles() {
        parentescos.forEach(parentesco => {
            const option_representante = document.createElement("option")
            option_representante.value = parentesco
            option_representante.textContent = parentesco
            parestenco_representante.append(option_representante)
            
            const option_otrorepresentante = document.createElement("option")
            option_otrorepresentante.value = parentesco
            option_otrorepresentante.textContent = parentesco
            otroparestenco.append(option_otrorepresentante)
        });
    }
    parentesco_controles();

    function Paises() {
        pais_nacimiento.innerHTML = "<option disabled selected hidden>Elija el País</option>";

        paises.forEach(paises => {
            const opcion = document.createElement("option");
            opcion.value = paises;
            opcion.textContent = paises;
            pais_nacimiento.appendChild(opcion);
        });
    }
    Paises();

    pais_nacimiento.addEventListener("change", function () {
        let pais_seleccionado = pais_nacimiento.options[pais_nacimiento.selectedIndex];

        let pais = pais_seleccionado.value;

        if (pais !== "" && pais !== "Elije una opción") {

            if (pais !== "Venezuela") {
                estado_nacimiento.hidden = true;
                municipio_nacimiento.hidden = true;
                parroquia_nacimiento.hidden = true;

                estado_novzla.hidden = false;
                municipio_novzla.hidden = false;
                parroquia_novzla.hidden = false;
            } else {
                estado_nacimiento.hidden = false;
                municipio_nacimiento.hidden = false;
                parroquia_nacimiento.hidden = false;

                estado_novzla.hidden = true;
                municipio_novzla.hidden = true;
                parroquia_novzla.hidden = true;
            }
        }
    });

    function EstadosNacimiento() {
        estado_nacimiento.innerHTML = '<option disabled selected hidden>Elije el Estado</option>';

        Estado.forEach(estado => {
            const option = document.createElement("option");
            option.value = estado;
            option.textContent = estado;
            estado_nacimiento.appendChild(option);
        });
    }
    EstadosNacimiento();

    function MunicipiosNacimiento(municipioSeleccionado = "") {
        const estado = estado_nacimiento.value;

        municipio_nacimiento.innerHTML = '<option disabled selected hidden>Elija el Municipio</option>';

        parroquia_nacimiento.innerHTML = '<option disabled selected hidden>Elije una Parroquia</option>';

        if (estado && municipiosPorEstado[estado]) {

            municipiosPorEstado[estado].forEach(municipio => {

                const option = document.createElement("option");
                option.value = municipio;
                option.textContent = municipio;

                if (municipio === municipioSeleccionado) {
                    option.selected = true;
                }

                municipio_nacimiento.appendChild(option);
            });
        }
    }

    function ParroquiasNacimiento(parroquiaSeleccionada = "") {
        const estado = estado_nacimiento.value;
        const municipio = municipio_nacimiento.value;

        parroquia_nacimiento.innerHTML = '<option disabled selected hidden>Elije una Parroquia</option>';

        if (estado && municipio && parroquiasPorMunicipio[estado] && parroquiasPorMunicipio[estado][municipio]) {
            parroquiasPorMunicipio[estado][municipio].forEach(parroquia => {
                const option = document.createElement("option");
                option.value = parroquia;
                option.textContent = parroquia;

                if (parroquia === parroquiaSeleccionada) {
                    option.selected = true;
                }

                parroquia_nacimiento.appendChild(option);

            });
        }
    }

    estado_nacimiento.addEventListener("change", () => {
        MunicipiosNacimiento();
    });

    municipio_nacimiento.addEventListener("change", () => {
        ParroquiasNacimiento();
    });

    function pais_proefesion_personal() {
        pais_profesion.innerHTML = "<option disabled selected hidden>Elije una opción</option>";

        Paises_laborales.forEach(codigo => {
            const option = document.createElement("option");
            option.value = codigo;
            option.textContent = codigo;
            pais_profesion.appendChild(option);
        });
    }
    pais_proefesion_personal();

    function MunicipioResidencia(municipioSeleccionado = "") {
        municipio_residencia.innerHTML = "";

        municipios.forEach(municipio => {
            const option = document.createElement("option");
            option.value = municipio;
            option.textContent = municipio;

            if (municipio === municipioSeleccionado) {
                option.selected = true;
            }

            municipio_residencia.appendChild(option);
        });
    }

    function ParroquiaResidencia(parroquiaSeleccionada = "") {
        const municipio = municipio_residencia.value;

        parroquia_residencia.innerHTML = "";

        if (parroquiasPorMunicipios[municipio]) {
            parroquiasPorMunicipios[municipio].forEach(parroquia => {
                const option = document.createElement("option");
                option.value = parroquia;
                option.textContent = parroquia;

                if (parroquia === parroquiaSeleccionada) {
                    option.selected = true;
                }

                parroquia_residencia.appendChild(option);
            });
        }
    }
    MunicipioResidencia();

    municipio_residencia.addEventListener("change", () => {
        ParroquiaResidencia();
    });

    formulario_busqueda_usuario.addEventListener("submit", async (e) => {
        e.preventDefault()
        try {
            const formulario = new FormData(formulario_busqueda_usuario)  
            const respuesta = await fetch("/buscar_datos_usuario/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            // Datos Básicos
            id_seleccionado.value = resultado.usuario.id_usuario
            nombres_actualizar_usuario.value = resultado.usuario.nombres
            apellidos_actualizar_usuario.value = resultado.usuario.apellidos
            
            const option_genero = document.createElement("option")
            option_genero.value = resultado.usuario.genero
            option_genero.textContent = resultado.usuario.genero
            option_genero.selected = true
            option_genero.hidden = true
            genero_actualizar_usuario.append(option_genero)
            
            const [nacionalidad, cedula] = resultado.usuario.cedula_identidad.split("-")

            const option_nacionalidad = document.createElement("option")
            option_nacionalidad.value = nacionalidad
            option_nacionalidad.textContent = nacionalidad
            option_nacionalidad.selected = true
            option_nacionalidad.hidden = true
            nacionalidad_actualizar_usuario.append(option_nacionalidad)

            cedula_identidad_actualizar_usuario.value = cedula

            const option_estado_civil = document.createElement("option")
            option_estado_civil.value = resultado.usuario.estado_civil
            option_estado_civil.textContent = resultado.usuario.estado_civil
            option_estado_civil.selected = true
            option_estado_civil.hidden = true
            estado_civil_actualizar_usuario.append(option_estado_civil)

            // Contacto
            let prefijo_principal = resultado.contacto.telefono_personal.slice(0,4)
            let num_telefonico_principal = resultado.contacto.telefono_personal.slice(4,11)

            const option_prefijo_principal = document.createElement("option")
            option_prefijo_principal.value = prefijo_principal
            option_prefijo_principal.textContent = prefijo_principal
            option_prefijo_principal.selected = true
            option_prefijo_principal.hidden = true
            prefijo_telefono_principal_actualizar.append(option_prefijo_principal)

            num_telefono_principal_actualizar.value = num_telefonico_principal

            if (resultado.contacto.telefono_suplete) {
                let prefijo_secundaria = resultado.contacto.telefono_suplete.slice(0,4)
                let num_telefonico_secundaria = resultado.contacto.telefono_suplete.slice(4,11)

                const option_prefijo_secundaria = document.createElement("option")
                option_prefijo_secundaria.value = prefijo_secundaria
                option_prefijo_secundaria.textContent = prefijo_secundaria
                option_prefijo_secundaria.selected = true
                option_prefijo_secundaria.hidden = true
                prefijo_telefono_secundaria_actualizar.append(option_prefijo_secundaria)

                prefijo_telefono_secundaria_actualizar.value = num_telefonico_secundaria
            }
            
            const [correo_principal, dominio_principal] = resultado.contacto.correo_electronico.split("@");
            
            console.log(correo_principal)
            console.log(dominio_principal)
            correo_principal_actualizar.value = correo_principal;

            const option_dominio_principal = document.createElement("option");
            option_dominio_principal.value = "@" + dominio_principal;
            option_dominio_principal.textContent = "@" + dominio_principal;
            option_dominio_principal.selected = true;
            option_dominio_principal.hidden = true;
            dominio_principal_actualizar.append(option_dominio_principal);


            const [correo_secundaria, dominio_secundaria] = resultado.contacto.correo_alternativo.split("@");

            correo_secundaria_actualizar.value = correo_secundaria;

            const option_dominio_secundaria = document.createElement("option");
            option_dominio_secundaria.value = "@" + dominio_secundaria;
            option_dominio_secundaria.textContent = "@" + dominio_secundaria;
            option_dominio_secundaria.selected = true;
            option_dominio_secundaria.hidden = true;

            dominio_secundaria_actualizar.append(option_dominio_secundaria);

            // Nacimiento            
            if (resultado.nacimiento.pais == "Venezuela") {
                pais_nacimiento.value = resultado.nacimiento.pais;
                estado_nacimiento.value = resultado.nacimiento.estado;
                MunicipiosNacimiento(resultado.nacimiento.municipio);

                ParroquiasNacimiento(resultado.nacimiento.parroquia);
                
                direccion_nacimiento.value = resultado.nacimiento.direccion_nacimiento;
                fecha_nacimiento.value = resultado.nacimiento.fecha_nacimiento;
            } else {
                pais_nacimiento.value = resultado.nacimiento.pais;
                estado_novzla.value = resultado.nacimiento.estado;
                municipio_novzla.value = resultado.nacimiento.municipio;
                parroquia_novzla.value = resultado.nacimiento.parroquia;
                direccion_nacimiento.value = resultado.nacimiento.direccion_nacimiento;
                fecha_nacimiento.value = resultado.nacimiento.fecha_nacimiento;
            }
                        
            // Residencia
            const option_condicion_residencia = document.createElement("option")
            option_condicion_residencia.value = resultado.residencia.condicion_residencia
            option_condicion_residencia.textContent = resultado.residencia.condicion_residencia
            option_condicion_residencia.selected = true
            option_condicion_residencia.hidden = true
            condicion_residencia.append(option_condicion_residencia)
            
            const option_municipio_residencia = document.createElement("option")
            option_municipio_residencia.value = resultado.residencia.municipio
            option_municipio_residencia.textContent = resultado.residencia.municipio
            option_municipio_residencia.selected = true
            option_municipio_residencia.hidden = true
            municipio_residencia.append(option_municipio_residencia)

            MunicipioResidencia(resultado.residencia.municipio);

            const option_parroquia_residencia = document.createElement("option")
            option_parroquia_residencia.value = resultado.residencia.parroquia
            option_parroquia_residencia.textContent = resultado.residencia.parroquia
            option_parroquia_residencia.selected = true
            option_parroquia_residencia.hidden = true
            parroquia_residencia.append(option_parroquia_residencia)
            
            ParroquiaResidencia(resultado.residencia.parroquia);

            direccion_domicilio.value = resultado.residencia.direccion_residencia

            if (resultado.perfil == "Estudiante") {
                // Secundaria    
                const option_tipos_secundaria = document.createElement("option")
                option_tipos_secundaria.value = resultado.secundaria.tipo_institucion
                option_tipos_secundaria.textContent = resultado.secundaria.tipo_institucion
                option_tipos_secundaria.selected = true
                option_tipos_secundaria.hidden = true
                tipos_secundaria.append(option_tipos_secundaria)

                nombre_liceo.value = resultado.secundaria.nombre_institucion
                fecha_grado.value = resultado.secundaria.fecha_grado
                codigo_sin_opsu.value = resultado.secundaria.codigo_sni_opsu

                // Representante
                if (resultado.padres && resultado.padres.length > 0) {
                    const representante = resultado.padres[0];

                    nombres_representante.value = representante.nombres;
                    apellidos_representante.value = representante.apellidos;

                    const nacionalidad = representante.cedula_identidad.slice(0, 1);
                    const cedula = representante.cedula_identidad.slice(2);

                    const option_nacionalidad_representante = document.createElement("option")
                    option_nacionalidad_representante.value = nacionalidad
                    option_nacionalidad_representante.textContent = nacionalidad
                    option_nacionalidad_representante.selected = true
                    option_nacionalidad_representante.hidden = true
                    nacionalidad_representante.append(option_nacionalidad_representante)

                    cedula_identidad_representante.value = cedula;

                    const prefijo = representante.telefono.slice(0, 4);
                    const telefono = representante.telefono.slice(4, 11);

                    const option_prefijo_telefono_representante = document.createElement("option")
                    option_prefijo_telefono_representante.value = prefijo
                    option_prefijo_telefono_representante.textContent = prefijo
                    option_prefijo_telefono_representante.selected = true
                    option_prefijo_telefono_representante.hidden = true
                    prefijo_telefono_representante.append(option_prefijo_telefono_representante);

                    numero_telefono_representante.value = telefono;
                    
                    const option_parentesco_representante = document.createElement("option")
                    option_parentesco_representante.value = representante.parentesco
                    option_parentesco_representante.textContent = representante.parentesco
                    option_parentesco_representante.selected = true
                    option_parentesco_representante.hidden = true
                    parestenco_representante.append(option_parentesco_representante);
                }

                if (resultado.padres && resultado.padres.length > 1) {

                    contenedor_otrorepresentante.style.display = "block";

                    const representante = resultado.padres[1];

                    nombres_otrorepresentante.value = representante.nombres;
                    apellidos_otrorepresentante.value = representante.apellidos;

                    const nacionalidad = representante.cedula_identidad.slice(0, 1);
                    const cedula = representante.cedula_identidad.slice(2);

                    const option_nacionalidad_representante = document.createElement("option")
                    option_nacionalidad_representante.value = nacionalidad
                    option_nacionalidad_representante.textContent = nacionalidad
                    option_nacionalidad_representante.selected = true
                    option_nacionalidad_representante.hidden = true
                    nacionalidad_representante.append(option_nacionalidad_representante)

                    cedula_identidad_otrorepresentante.value = cedula;

                    const prefijo = representante.telefono.slice(0, 4);
                    const telefono = representante.telefono.slice(4, 11);

                    const option_prefijo_telefono_representante = document.createElement("option")
                    option_prefijo_telefono_representante.value = prefijo
                    option_prefijo_telefono_representante.textContent = prefijo
                    option_prefijo_telefono_representante.selected = true
                    option_prefijo_telefono_representante.hidden = true
                    prefijo_telefono_representante.append(option_prefijo_telefono_representante);

                    numero_telefono_otrorepresentante.value = telefono;

                    const option_parentesco_representante = document.createElement("option")
                    option_parentesco_representante.value = representante.parentesco
                    option_parentesco_representante.textContent = representante.parentesco
                    option_parentesco_representante.selected = true
                    option_parentesco_representante.hidden = true
                    otroparestenco.append(option_parentesco_representante);
                } else {
                    contenedor_otrorepresentante.style.display = "none";
                }

                // Discapacidad
                codigo_carnet_dispacidad.value = resultado.discapacidad.codigo_carnet_discapacidad
                nro_registro_medico.value = resultado.discapacidad.nro_registro_medico
                
                const option_tipo_discapacidad = document.createElement("option")
                option_tipo_discapacidad.value = resultado.discapacidad.tipo_discapacidad
                option_tipo_discapacidad.textContent = resultado.discapacidad.tipo_discapacidad
                option_tipo_discapacidad.selected = true
                option_tipo_discapacidad.hidden = true
                tipos_discapacidad.append(option_tipo_discapacidad)
                
                const option_grado_discapacidad = document.createElement("option")
                option_grado_discapacidad.value = resultado.discapacidad.grado_discapacidad
                option_grado_discapacidad.textContent = resultado.discapacidad.grado_discapacidad
                option_grado_discapacidad.selected = true
                option_grado_discapacidad.hidden = true
                grado_discapacidad.append(option_grado_discapacidad)
                
                const option_causa_discapacidad= document.createElement("option")
                option_causa_discapacidad.value = resultado.discapacidad.causa_discapacidad
                option_causa_discapacidad.textContent = resultado.discapacidad.causa_discapacidad
                option_causa_discapacidad.selected = true
                option_causa_discapacidad.hidden = true
                causa_discapacidad.append(option_causa_discapacidad)
            } else {
                // Profesión
                profesion_usuario.value = resultado.profesion.profesion_pregrado
                universidad_usuario.value = resultado.profesion.universidad_egreso_pregrado

                const option_pais_profesion = document.createElement("option")
                option_pais_profesion.value = resultado.profesion.pais_profesion_pregrado
                option_pais_profesion.textContent = resultado.profesion.pais_profesion_pregrado
                option_pais_profesion.selected = true
                option_pais_profesion.hidden = true
                pais_profesion.append(option_pais_profesion)
            }

            if (resultado.perfil === "Estudiante") {
                bloqueProfesion.style.display = "none";

                bloqueSecundaria.style.display = "block";
                bloqueRepresentante.style.display = "block";
                bloqueDiscapacidad.style.display = "block";
            } else {
                bloqueProfesion.style.display = "block";

                bloqueSecundaria.style.display = "none";
                bloqueRepresentante.style.display = "none";
                bloqueDiscapacidad.style.display = "none";
            }
        } catch (error) {
            console.error(error);
        }     
    });

    formulario_actualizar_usuario.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            const formulario = new FormData(formulario_actualizar_usuario)  
            const respuesta = await fetch("/modulo_actualizar_usuarios/", {
                method: "POST",
                body: formulario
            });
            const resultado = await respuesta.json();
            console.log(resultado);

            if (resultado.estado === "success") {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            } else {
                Swal.fire({
                    text: resultado.descripcion,
                    icon: resultado.icon,
                    allowOutsideClick: false,
                    allowEscapeKey: false
                });
            }
        } catch (error) {
            console.error(error);
        }
    });

});