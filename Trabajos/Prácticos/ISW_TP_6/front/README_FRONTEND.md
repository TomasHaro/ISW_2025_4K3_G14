💻 Frontend – EcoHarmony Park

📘 Descripción General
El frontend de EcoHarmony Park implementa la interfaz web que permite a los usuarios realizar el proceso completo de inscripción a actividades recreativas y educativas del parque.
•	Desarrollado con Next.js (React + TypeScript).
•	Consume los servicios REST del backend en FastAPI, conectándose a través de http://localhost:8000/api.
•	Su diseño prioriza la claridad y la experiencia de usuario, guiándolo paso a paso en el proceso.
________________________________________

🪄 Flujo del Usuario
1.	Selección de actividad
2.	Elección de horario con cupos disponibles
3.	Carga de datos personales y aceptación de términos
4.	Confirmación de inscripción exitosa
Cada paso está controlado mediante validaciones en tiempo real para garantizar que los datos ingresados sean correctos y coherentes.
________________________________________

⚙️ Funcionalidad Principal
El frontend permite:
•	Listar actividades disponibles del parque, mostrando su descripción, requisitos y términos.
•	Visualizar horarios y cupos de cada actividad.
•	Registrar una inscripción completa de uno o varios participantes.
•	Validar datos del formulario, incluyendo:
o	DNIs duplicados
o	Rangos de edad
o	Talles de vestimenta cuando sean requeridos
•	Confirmar visualmente la inscripción, mostrando un resumen claro del proceso.
💡 Toda la comunicación se realiza mediante peticiones HTTP a la API REST del backend en
http://localhost:8000/api
________________________________________

🧠 Flujo de Uso
•	El usuario accede a la aplicación web en http://localhost:3000.
•	El sistema obtiene las actividades desde /api/actividades.
•	Al seleccionar una actividad, consulta los horarios en /api/actividades/{id}/horarios.
•	El usuario completa sus datos y acepta los términos.
•	Finalmente, el formulario se envía a POST /api/inscripciones.
•	El sistema responde confirmando el registro y mostrando los datos del turno.
________________________________________

🧩 Endpoints Consumidos
Método	Ruta	Descripción
GET	/api/actividades	Obtiene las actividades disponibles del parque.
GET	/api/actividades/{id}/horarios	Lista los horarios y cupos de una actividad específica.
POST	/api/inscripciones	Registra la inscripción de uno o más participantes.
GET	/api/health	Verifica el estado del servidor.
________________________________________

⚙️ Tecnologías Utilizadas
•	Next.js 15
•	React 19 + TypeScript
•	Tailwind CSS + shadcn/ui
•	Lucide-react (iconografía)
•	Geist Fonts
•	Integración directa con API FastAPI (Python)
________________________________________

🧩 Estructura del Proyecto
front/
├── app/
│   ├── layout.tsx              # Layout raíz con fuentes y estilos globales
│   ├── page.tsx                # Página principal (flujo de inscripción)
│   └── globals.css             # Estilos base y variables CSS
├── components/
│   └── activity-registration.tsx  # Componente principal de inscripción
├── public/                     # Recursos estáticos
├── package.json
└── README.md
________________________________________

🚀 Ejecución Local
1️⃣ Requisitos previos
•	Node.js v18+
•	npm o yarn
•	Backend levantado en http://localhost:8000/api
________________________________________

2️⃣ Instalar dependencias
Desde la carpeta front/:
npm install --legacy-peer-deps
🔹 Este comando no modifica el proyecto:
simplemente ignora conflictos menores de librerías entre React 19 y dependencias previas.
________________________________________

3️⃣ Configurar variables de entorno
Crear un archivo .env.local en la raíz de front/ con:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
🧩 Esta variable permite que el frontend se comunique correctamente con la API local del backend.
________________________________________

4️⃣ Levantar el entorno de desarrollo
npm run dev
Luego abrir en el navegador:
👉 http://localhost:3000
________________________________________

🌐 Integración con el Backend
El frontend interactúa directamente con el backend de FastAPI a través de peticiones REST:
•	Backend corriendo en: http://localhost:8000
•	Comunicación bajo la ruta base: /api
•	CORS habilitado para http://localhost:3000
•	Toda acción del usuario (actividad, horario, inscripción) impacta sobre la base de datos ecoharmony.db
⚙️ En otras palabras, el flujo completo del usuario en la web queda reflejado automáticamente en la base de datos del sistema.
________________________________________

📸 Funcionalidades Destacadas
•	Interfaz moderna, intuitiva y responsive
•	Validaciones en tiempo real: nombre, DNI, edad y talle
•	Prevención automática de DNIs duplicados
•	Mensajes claros de error y éxito
•	Indicadores visuales de estado (cargando, confirmado, error)
•	Navegación fluida entre pasos del proceso de inscripción
________________________________________

👨‍🎓 Datos de Cátedra
Proyecto: EcoHarmony Park
Materia: Ingeniería y Calidad de Software – 4K3
Universidad: UTN – Facultad Regional Córdoba
Año: 2025 – 2° Cuatrimestre
Autores (Grupo 14):
•	Riera, Martín Fernando – 91746
•	González Bernahola, Alessandro Tomás – 92950
•	Sangenis Libra, Valentino – 90153
•	Magris, Santino Alejandro – 91999
•	Haro Monforte, Tomás – 83204
•	Caliva, Ariel Enrique – 69777
•	Patriarca, Ignacio – 91025
•	Simes, Juan Mateo – 96074
•	Dilewski, Ignacio Nicolás – 97662
