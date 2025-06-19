Guía de Pruebas con Postman - Sistema de Votaciones

Configuración Inicial

1. Importar la Colección
    1. Abre Postman
    2. Click en "Import" 
    3. Copia y pega el JSON de la colección
    4. La colección "Sistema de Votaciones API" aparecerá en tu workspace

2. Configurar Variables de Entorno
    La colección usa la variable `{{base_url}}` que por defecto es `http://localhost:8000`

    Para cambiar la URL:
    1. Click en el ícono de "Environment" 
    2. Crea un nuevo environment llamado "Voting System"
    3. Agrega la variable:
    - Variable: `base_url`
    - Value: `http://localhost:8000`

Secuencia de Pruebas Recomendada

Fase 1: Verificación Inicial

    1. Health Check
    2. API Root

Fase 2: Crear Datos Base

    3. Crear Votante - Juan Pérez
    4. Crear Votante - María García  
    5. Crear Votante - Carlos López
    6. Crear Candidato - Ana Martínez
    7. Crear Candidato - Roberto Silva
    8. Crear Candidato - Elena Torres

Fase 3: Consultar Datos

    9. Obtener Todos los Votantes
    10. Obtener Todos los Candidatos
    11. Obtener Votante por ID
    12. Obtener Candidato por ID

Fase 4: Emitir Votos

    13. Emitir Voto - Votante 1 por Candidato 1
    14. Emitir Voto - Votante 2 por Candidato 2
    15. Obtener Todos los Votos
    16. Obtener Estadísticas de Votación

Fase 5: Probar Validaciones

    17. Verificar Votante-Candidato
    18. Error - Email Duplicado
    19. Error - Votar Dos Veces
    20. Error - Votante Inexistente
    21. Error - Candidato Inexistente

Ejemplos Detallados por Endpoint

1. Health Check
- Método: GET
- URL: `http://localhost:8000/health`
- Respuesta Esperada:
    json
    {
    "status": "healthy",
    "message": "Sistema de votaciones funcionando correctamente"
    }

2. Crear Votante
- Método: POST
- URL: `http://localhost:8000/voters`
- Headers: `Content-Type: application/json`
- Body:
    json
    {
    "name": "Juan Pérez",
    "email": "juan.perez@example.com"
    }

- Respuesta Esperada:
    json
    {
    "id": 1,
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "has_voted": false
    }

3. Crear Candidato
- Método: POST
- URL: `http://localhost:8000/candidates`
- Headers: `Content-Type: application/json`
- Body:
    json
    {
    "name": "Ana Martínez",
    "party": "Partido Democrático"
    }

    - Respuesta Esperada:
    json
    {
    "id": 1,
    "name": "Ana Martínez",
    "party": "Partido Democrático",
    "votes_count": 0
    }


4. Emitir Voto
- Método: POST
- URL: `http://localhost:8000/votes`
- Headers: `Content-Type: application/json`
- Body:
    json
    {
    "voter_id": 1,
    "candidate_id": 1
    }

    - Respuesta Esperada:
    json
    {
    "id": 1,
    "voter_id": 1,
    "candidate_id": 1
    }


5. Obtener Estadísticas
- Método: GET
- URL: `http://localhost:8000/votes/statistics`
- Respuesta Esperada:
    json
    {
    "total_voters_who_voted": 2,
    "candidates_statistics": [
        {
        "candidate_id": 1,
        "candidate_name": "Ana Martínez",
        "party": "Partido Democrático",
        "total_votes": 1,
        "vote_percentage": 50.0
        },
        {
        "candidate_id": 2,
        "candidate_name": "Roberto Silva", 
        "party": "Partido Liberal",
        "total_votes": 1,
        "vote_percentage": 50.0
        }
    ]
    }


Casos de Error a Probar

Error - Email Duplicado
    Intenta crear un votante con un email que ya existe:
    json
    {
    "name": "Juan Pérez Duplicado",
    "email": "juan.perez@example.com"
    }

    Respuesta: `400 Bad Request - "Email ya registrado"`

 Error - Votar Dos Veces
    Intenta que el mismo votante vote nuevamente:
    json
    {
    "voter_id": 1,
    "candidate_id": 2
    }

    Respuesta: `400 Bad Request - "El votante ya ha emitido su voto"`

    Error - Votante Inexistente
    json
    {
    "voter_id": 999,
    "candidate_id": 1
    }

Respuesta: `404 Not Found - "Votante no encontrado"`

Pruebas con Paginación

Obtener Votantes con Paginación
    - URL: `http://localhost:8000/voters?skip=0&limit=2`
    - Descripción: Obtiene los primeros 2 votantes

#Obtener Candidatos con Paginación  
    - URL: `http://localhost:8000/candidates?skip=1&limit=1`
    - Descripción: Obtiene 1 candidato saltando el primero

Validaciones Especiales

#Verificar Votante-Candidato
    - URL: `http://localhost:8000/validations/voter-candidate-check/1`
    - Descripción: Verifica si un votante puede votar (no es candidato)

Tips para las Pruebas

1. Orden Importante: Ejecuta las pruebas en el orden sugerido
2. IDs Dinámicos: Los IDs se generan automáticamente, ajusta según sea necesario
3. Estado de BD: Reinicia la aplicación para limpiar la base de datos
4. Errores Esperados: Los casos de error deben fallar para validar el sistema
5. Estadísticas: Las estadísticas cambian con cada voto emitido

Comandos Útiles

Limpiar Base de Datos
bash
Eliminar archivo de base de datos
    del voting_system.db  - Windows
    rm voting_system.db   - Linux/Mac

Reiniciar la aplicación
    python main.py


Verificar Base de Datos
    bash
    sqlite3 voting_system.db
    .tables
    SELECT * FROM voters;
    SELECT * FROM candidates;
    SELECT * FROM votes;
    .quit
