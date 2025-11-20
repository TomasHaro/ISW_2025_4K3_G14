# 🐍 Backend – EcoHarmony Park

## 📘 Descripción General
El backend de **EcoHarmony Park** implementa los servicios necesarios para gestionar el proceso completo de **inscripción a actividades del parque**, desde la consulta de actividades y horarios disponibles hasta el registro final de los participantes.

Está desarrollado con **FastAPI (Python)** y utiliza una base de datos **SQLite (`ecoharmony.db`)** para almacenar toda la información persistente.  
El sistema fue diseñado bajo una **arquitectura modular**, separando la lógica de negocio, la persistencia de datos y la interfaz con el frontend.

---

## ⚙️ Funcionalidad Principal
El backend expone una **API REST** que permite:

1. **Listar actividades disponibles** del parque, incluyendo su descripción, si requieren talle y sus términos y condiciones.
2. **Obtener los horarios y cupos** disponibles para una actividad específica.
3. **Registrar inscripciones** de uno o más participantes a una actividad y horario, aplicando validaciones de negocio.
4. **Verificar el estado del servidor** mediante un endpoint de salud.

Estos servicios son consumidos por el frontend (Next.js), que guía al usuario a través del proceso de selección de actividad, horario y carga de datos personales.

---

## 🧠 Flujo de Lógica y Validaciones
Cuando el usuario completa una inscripción, el backend realiza los siguientes pasos:

1. **Validación de datos:**
   - Verifica que la actividad y el horario existan.
   - Comprueba que los términos y condiciones hayan sido aceptados.
   - Controla que los participantes tengan nombre, DNI y edad válidos.
   - Evita DNIs duplicados dentro de la misma inscripción.
   - En caso de actividades que lo requieran, exige el talle de vestimenta.

2. **Gestión de cupos:**
   - Verifica que existan suficientes cupos para la cantidad de participantes.
   - Si la inscripción es válida, **registra los participantes** y **decrementa los cupos disponibles** del horario elegido.

3. **Persistencia:**
   - Las operaciones se realizan dentro de una **transacción**, garantizando la consistencia de los datos.
   - Si ocurre algún error, la transacción se revierte automáticamente.

4. **Respuesta:**
   - Devuelve un mensaje JSON con el resultado de la inscripción, informando si fue exitosa o si ocurrió algún problema.

---

## 📡 Endpoints Principales

| Método | Ruta | Descripción |
|:------:|:--------------------------------------|:---------------------------------------------|
| `GET` | `/api/actividades` | Devuelve la lista de actividades disponibles en el parque. |
| `GET` | `/api/actividades/{id}/horarios` | Devuelve los horarios y cupos disponibles para una actividad. |
| `POST` | `/api/inscripciones` | Crea una nueva inscripción con validaciones completas. |
| `GET` | `/api/health` | Verifica el estado del servidor (ping). |

---

## 🧩 Ejemplo de Uso

### 📤 Request – Inscripción
``json
{
  "nombre_actividad": "Tirolesa",
  "horario": "10:00",
  "participantes": [
    { "nombre": "Valentino Sangenis Libra", "dni": "23222222", "edad": 22, "talle": "S" }
  ],
  "aceptar_terminos": true
}

📥 Response – Éxito
{
  "exito": true,
  "mensaje": "Inscripción realizada con éxito."
}

📥 Response – Error (ejemplo)
{
  "exito": false,
  "mensaje": "No hay cupos suficientes para ese horario."
}

⚙️ Ejecución Local

Para levantar el servidor localmente:

cd back
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000


URL base: http://127.0.0.1:8000

Documentación interactiva (Swagger): http://127.0.0.1:8000/docs

🧭 Conexión con el Frontend

El frontend consume esta API a través de los endpoints definidos.
La comunicación se realiza por medio de peticiones HTTP al dominio local http://localhost:8000/api, con CORS habilitado para localhost:3000.
De esta manera, las acciones realizadas desde la interfaz web (selección de actividad, horario y registro de datos) impactan directamente sobre la base de datos del sistema.

🌱 Observaciones Técnicas

Arquitectura modular: capas de Modelo, Servicio y Persistencia.

Uso de Pydantic para la validación de datos en los endpoints.

Implementación de transacciones en la base de datos para mantener la integridad de los cupos.

Manejo de errores controlados mediante excepciones HTTP en FastAPI.

Base de datos SQLite, liviana y de fácil integración para entornos académicos y de prueba.

👨‍🎓 Datos de Cátedra

Proyecto: EcoHarmony Park
Materia: Ingeniería y Calidad de Software – 4K3
Universidad: UTN – Facultad Regional Córdoba
Año: 2025 – 2° Cuatrimestre

Autores (Grupo 14):

Riera, Martin Fernando – 91746

González Bernahola, Alessandro Tomas – 92950

Sangenis Libra, Valentino – 90153

Magris, Santino Alejandro – 91999

Haro Monforte, Tomás – 83204

Caliva, Ariel Enrique – 69777

Patriarca, Ignacio – 91025

Simes, Juan Mateo – 96074

Dilewski, Ignacio Nicolás – 97662
