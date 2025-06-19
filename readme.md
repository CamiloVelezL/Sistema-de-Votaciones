# Sistema de Votaciones - FastAPI

API RESTful para gestionar un sistema de votaciones desarrollada con FastAPI y SQLAlchemy.

## Características Principales

- **Gestión de Votantes**: Registro, consulta y eliminación de votantes
- **Gestión de Candidatos**: Registro, consulta y eliminación de candidatos  
- **Sistema de Votación**: Emisión de votos con validaciones de integridad
- **Estadísticas**: Reportes completos de resultados de votación
- **Validaciones**: Verificación de reglas de negocio y integridad de datos

## Requisitos Técnicos Implementados

### Base de Datos
- **SQLite** como base de datos (fácil para desarrollo y pruebas)
- **SQLAlchemy** como ORM
- Modelos: `Voter`, `Candidate`, `Vote`

### Validaciones Implementadas
1. **Votantes y Candidatos**: Un votante no puede ser candidato y viceversa
2. **Emisión de Votos**: Un votante no puede votar si ya ha votado previamente
3. **Integridad de Datos**: El campo `has_voted` se actualiza automáticamente
4. **Conteo Correcto**: Los votos se cuentan correctamente en las estadísticas

### Endpoints Implementados

#### Votantes
- `POST /voters` - Registrar nuevo votante
- `GET /voters` - Obtener lista de votantes
- `GET /voters/{id}` - Obtener detalles de votante
- `DELETE /voters/{id}` - Eliminar votante

#### Candidatos  
- `POST /candidates` - Registrar nuevo candidato
- `GET /candidates` - Obtener lista de candidatos
- `GET /candidates/{id}` - Obtener detalles de candidato
- `DELETE /candidates/{id}` - Eliminar candidato

#### Votos
- `POST /votes` - Emitir un voto
- `GET /votes` - Obtener todos los votos
- `GET /votes/statistics` - Obtener estadísticas de votación

#### Extras
- `GET /validations/voter-candidate-check/{voter_id}` - Verificar validaciones
- `GET /health` - Verificación de salud
- `GET /` - Información de la API

## Instalación y Ejecución

### 1. Clonar o descargar los archivos
```bash
# Crear directorio del proyecto
mkdir voting-system
cd voting-system

# Copiar los archivos: main.py, requirements.txt, README.md
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python main.py
```

La API estará disponible en: `http://localhost:8000`

### 5. Documentación interactiva
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Ejemplos de Uso

### 1. Registrar un votante
```bash
curl -X POST "http://localhost:8000/voters" \
     -H "Content-Type: application/json" \
     -d '{"name": "Juan Pérez", "email": "juan@example.com"}'
```

### 2. Registrar un candidato
```bash
curl -X POST "http://localhost:8000/candidates" \
     -H "Content-Type: application/json" \
     -d '{"name": "María García", "party": "Partido Democrático"}'
```

### 3. Emitir un voto
```bash
curl -X POST "http://localhost:8000/votes" \
     -H "Content-Type: application/json" \
     -d '{"voter_id": 1, "candidate_id": 1}'
```

### 4. Obtener estadísticas
```bash
curl -X GET "http://localhost:8000/votes/statistics"
```

## Estructura del Proyecto

```
voting-system/
├── main.py              # Código principal de la API
├── requirements.txt     # Dependencias del proyecto
├── README.md           # Documentación
└── voting_system.db    # Base de datos SQLite (se crea automáticamente)
```

## Modelos de Datos

### Voter (Votante)
- `id`: ID único autogenerado
- `name`: Nombre del votante (obligatorio)
- `email`: Correo electrónico único (obligatorio)  
- `has_voted`: Booleano que indica si ya votó (por defecto: false)

### Candidate (Candidato)
- `id`: ID único autogenerado
- `name`: Nombre del candidato (obligatorio)
- `party`: Partido político (opcional)
- `votes_count`: Número de votos recibidos (por defecto: 0)

### Vote (Voto)
- `id`: ID único autogenerado
- `voter_id`: ID del votante (relación)
- `candidate_id`: ID del candidato seleccionado (relación)

## Características Adicionales

### Autenticación JWT
El código incluye la estructura básica para autenticación JWT (descomentada para simplicidad en desarrollo).

### Paginación
Los endpoints de listado incluyen parámetros `skip` y `limit` para paginación.

### Manejo de Errores
Respuestas HTTP apropiadas con mensajes de error descriptivos.

### Filtrado y Validaciones
Uso de validaciones de patrones RESTful y manejo correcto de errores.

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validación de datos y serialización
- **SQLite**: Base de datos ligera
- **Uvicorn**: Servidor ASGI

## Pruebas

Para probar la API se puede usar:
- **Swagger UI** integrado en `/docs`
- **Postman** o **Thunder Client**
- **curl** desde línea de comandos
- **pytest** para pruebas automatizadas (no incluidas)
