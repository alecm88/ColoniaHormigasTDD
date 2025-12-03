# Subsistema de Hormiga Reina - Queen Ant Subsystem

**Proyecto Académico**: Sistema modular de simulación de colonia de hormigas implementado con metodologías TDD y BDD.

Este proyecto implementa el **Subsistema de Hormiga Reina** como parte de un sistema distribuido de simulación de colonia de hormigas. El subsistema es responsable de la gestión, asignación y control de hormigas para otros subsistemas (Comunicación, Recolección, Defensa).

## Características Académicas Principales

- **✅ R1 - Dar Hormiga**: Asignación de hormigas a subsistemas solicitantes con validación de prioridades
- **✅ R2 - Devolver Hormiga**: Retorno de hormigas con estado (exitosa/muerta, con/sin comida)
- **✅ R3 - Emergencia**: Reasignación automática basada en prioridades durante crisis
- **✅ Gestión de Recursos**: Stock de comida, capacidad máxima configurable, tiempo de vida
- **✅ Priorización**: Defense (1) > Communication (2) > Collection (3)
- **✅ Stretch Goals**: Expiración de hormigas, manejo de crisis, gestión robusta

## Subsistemas Externos (Mocks)

- **Communication** (Prioridad 2): Gestión de mensajes y comunicación
- **Collection** (Prioridad 3): Recolección de recursos y comida
- **Defense** (Prioridad 1): Defensa de la colonia - máxima prioridad

## Arquitectura del Sistema

- **Ciclo de Vida**: Hormigas con tiempo de vida configurable (default: 1.5 minutos)
- **Estados**: FREE → ASSIGNED → DEAD/FREE
- **Recursos**: Stock de comida configurable (default: 1 unidad/hormiga) 
- **Capacidad**: Máximo configurable de hormigas simultáneas (default: 100)
- **Tiempo de vida**: Tiempo de vida configurable por hormiga (default: 1.5min)
- **Testing**: Comprehensive TDD + BDD coverage (140+ tests, 6 scenarios)

## Estructura del Proyecto

```
ColoniaHormigasTDD/
├── src/
│   ├── __init__.py
│   ├── ant.py              # Modelo de hormiga con estados y ciclo de vida
│   ├── colony.py           # Gestión de colonia con asignaciones y emergencias
│   ├── service.py          # Servicio de manejo de mensajes (Integracion con Comunicacion)
│   ├── subsystems.py       # Definición de subsistemas externos
│   ├── models.py           # Definición de modelos Pydantic para el API
│   └── main.py             # API FastAPI del Subsistema Hormiga Reina
├── tests/
│   ├── __init__.py
│   ├── test_ant.py             # Tests unitarios modelo base
│   ├── test_ant_extended.py    # Tests unitarios funcionalidad extendida
│   ├── test_colony.py          # Tests unitarios colonia base
│   ├── test_colony_extended.py # Tests unitarios gestión avanzada
│   ├── test_subsystems.py      # Tests unitarios subsistemas
│   ├── test_api.py             # Tests integración API base
│   ├── test_api_integration.py # Tests integración API comunicación
│   └── test_api_extended.py    # Tests integración API completa
├── features/
│   ├── ant_colony.feature      # Especificaciones BDD - Escenarios académicos
│   └── steps/
│       └── colony_steps.py     # Definiciones de pasos BDD
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── Makefile
└── README.md
```

## API Endpoints - Subsistema Hormiga Reina

### 🐜 Endpoints Principales (Requisitos Académicos)

#### Iniciar servicio de revisión de mensajes (Requiere servicio de comunicación)
```http
POST /service?interval=5&run_for_minutes=5&activate=true

#### Detener servicio de revisión de mensajes (Requiere servicio de comunicación)
```http
POST /service?activate=false


#### R1: Dar Hormiga
```http
POST /ants/request
Content-Type: application/json

{
  "subsystem_name": "S05_DEF",
  "priority": 1,
  "estimated_duration_seconds": 60
}
```

#### R2: Devolver Hormiga
```http
POST /ants/return
Content-Type: application/json

{
  "ant_id": "uuid-string",
  "returned_with_food": true,
  "died_in_mission": false
}
```

#### R3: Solicitar Emergencia
```http
POST /ants/emergency
Content-Type: application/json

{
  "requesting_subsystem": "S05_DEF",
  "number_needed": 5,
  "max_wait_seconds": 30
}
```

### 📊 Endpoints de Estado y Consulta

- `GET /` - Información del subsistema Hormiga Reina
- `GET /colony/status/comprehensive` - Estado detallado del hormiguero
- `GET /ants?state=free|assigned|dead` - Hormigas filtradas por estado
- `GET /ants/{ant_id}` - Información específica de una hormiga
- `GET /subsystems` - Subsistemas disponibles y prioridades

### ⚙️ Endpoints de Configuración

- `PUT /colony/config?max_ants=100&food_stock=1000&ant_lifespan_minutes=1.5`
- `POST /colony/food/add?amount=100` - Agregar comida al stock
- `POST /colony/cleanup` - Limpiar hormigas muertas manualmente

### 📖 Documentación API Interactiva

**Ejecuta el servidor primero:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Luego puedes acceder a la documentación completa de la API:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) - Interfaz interactiva para probar endpoints
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) - Documentación alternativa estilo ReDoc
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) - Esquema OpenAPI en formato JSON

La documentación incluye:
- ✅ Especificaciones completas de todos los endpoints (R1, R2, R3)
- ✅ Modelos de request/response con ejemplos
- ✅ Validación automática de parámetros
- ✅ Códigos de respuesta y mensajes de error
- ✅ Interfaz de pruebas integrada para todos los equipos

### ⚠️ Guía Rápida para Equipos

**Valores de subsistemas (case-sensitive):**
```json
{
  "subsystem_name": "S05_DEF"      // ✅ Correcto
  "subsystem_name": "Test"      // ❌ Error 422
  "subsystem_name": "S01_COM" // ✅ Correcto
  "subsystem_name": "S02_REC"    // ✅ Correcto
}
```

**URLs correctas:**
- ✅ `http://localhost:8000/ants/request`
- ❌ `http://localhost/ants/request` (falta puerto)

**Configuraciones importantes:**
- **CORS habilitado**: Funciona desde Swagger UI y herramientas externas
- **Validación estricta**: Todos los parámetros son validados automáticamente
- **Documentación en vivo**: Swagger UI se actualiza automáticamente

## Installation & Usage

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run unit tests:**
   ```bash
   pytest tests/ -v
   ```
   
3. **Run coverage tests:**
   ```bash
   pytest --cov=. tests/
   ```

4. **Run BDD tests:**
   ```bash
   behave features/
   ```

5. **Start the development server:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Using Docker

1. **Build and run with Docker:**
   ```bash
   docker build -t ant-colony-api .
   docker run -p 8000:8000 ant-colony-api
   ```

2. **Or use docker-compose:**
   ```bash
   docker-compose up -d
   ```

3. **For production with nginx:**
   ```bash
   docker-compose --profile production up -d
   ```

### Using Makefile

```bash
# Install dependencies
make install

# Run all tests
make test

# Run development server
make run-dev

# Build Docker image
make build

# Run with Docker
make run

# Start with docker-compose
make docker-up

# View logs
make docker-logs

# Clean up
make clean
```

## Ejemplos de Uso de la API

### R1: Solicitar Hormiga para Defensa
```bash
curl -X POST http://localhost:8000/ants/request \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "defense",
    "priority": 1,
    "estimated_duration_seconds": 30
  }'
```

⚠️ **Importante**: Usar `"defense"` (minúscula), no `"Defense"`

Respuesta exitosa:
```json
{
  "message": "Ant assigned to Defense",
  "assignment_successful": true,
  "ant": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "birth_time": "2024-01-15T10:30:00.000000",
    "death_time": "2024-01-15T10:31:30.000000",
    "is_alive": true,
    "age_seconds": 2.5,
    "remaining_life_seconds": 87.5,
    "state": "assigned",
    "assigned_to": "defense",
    "assignment_time": "2024-01-15T10:30:02.500000",
    "wait_time_seconds": 10
  }
}
```

### R2: Devolver Hormiga con Comida
```bash
curl -X POST http://localhost:8000/ants/return \
  -H "Content-Type: application/json" \
  -d '{
    "ant_id": "550e8400-e29b-41d4-a716-446655440000",
    "returned_with_food": true,
    "died_in_mission": false
  }'
```

Respuesta:
```json
{
  "message": "Ant 550e8400-e29b-41d4-a716-446655440000 returned with food",
  "food_gained": true,
  "ant_died": false
}
```

### R3: Solicitar Hormigas de Emergencia
```bash
curl -X POST http://localhost:8000/ants/emergency \
  -H "Content-Type: application/json" \
  -d '{
    "requesting_subsystem": "defense",
    "number_needed": 3,
    "max_wait_seconds": 30
  }'
```

⚠️ **Importante**: Usar `"defense"` (minúscula), no `"Defense"`

### Estado Comprehensive del Hormiguero
```bash
curl http://localhost:8000/colony/status/comprehensive
```

Respuesta:
```json
{
  "total_ants": 15,
  "alive_ants": 12,
  "free_ants": 5,
  "assigned_ants": 7,
  "dead_ants": 3,
  "max_ants": 100,
  "food_stock": 850,
  "can_create_more": true,
  "emergency_mode": false,
  "ants_by_subsystem": {
    "defense": 3,
    "communication": 2,
    "collection": 2
  },
  "ant_lifespan_minutes": 1.5
}
```

### Configurar Parámetros de la Colonia
```bash
curl -X PUT "http://localhost:8000/colony/config?max_ants=150&food_stock=2000&ant_lifespan_minutes=2.0"
```

## Testing - Metodología TDD + BDD

### 🧪 Tests Unitarios (TDD) - 68+ Tests
```bash
# Ejecutar todos los tests unitarios
pytest tests/ -v

# Tests específicos por módulo
pytest tests/test_subsystems.py -v          # Gestión de subsistemas
pytest tests/test_ant_extended.py -v        # Modelo extendido de hormigas
pytest tests/test_colony_extended.py -v     # Gestión avanzada de colonia
pytest tests/test_api_extended.py -v        # API del Subsistema Hormiga Reina
```

**Cobertura de Tests Unitarios:**
- **Subsistemas**: Validación de prioridades, identificación, jerarquías
- **Modelo de Hormiga**: Estados, ciclo de vida, asignaciones, validación de tareas
- **Gestión de Colonia**: Asignaciones, emergencias, reasignación, stock de comida
- **APIs**: Endpoints académicos, validaciones, manejo de errores, integración

### 🎭 Tests BDD (Comportamiento) - 6 Scenarios
```bash
# Ejecutar escenarios BDD
behave features/
```

**Escenarios Académicos Implementados:**
1. **Asignación exitosa** a subsistemas conocidos con validación de recursos
2. **Rechazo de subsistemas desconocidos** con mensajes de error apropiados
3. **Gestión de recursos insuficientes** (comida insuficiente)
4. **Retorno de hormigas exitoso** con incremento de comida
5. **Muerte en misión** y marcado apropiado de estado
6. **Solicitudes de emergencia** con asignación automática de hormigas disponibles

### 📊 Cobertura y Calidad

- **Cobertura ≥ 80%** según requisitos académicos
- **TDD Red-Green-Refactor** aplicado consistentemente
- **BDD User Stories** validando comportamientos de negocio
- **Casos Edge** cubiertos: capacidad límite, recursos agotados, crisis
- **Validación de Prioridades** en todos los escenarios de reasignación

## Decisiones de Diseño Académicas

### 🏗️ Arquitectura del Subsistema
1. **Responsabilidad Única**: Solo gestión y asignación de hormigas
2. **Comunicación con Mocks**: Simula subsistemas externos sin implementarlos
3. **Prioridades Jerárquicas**: Defense(1) > Communication(2) > Collection(3)
4. **Estado Centralizado**: Toda la información en memoria (requisito académico)

### 🐜 Modelo de Hormigas
1. **Tiempo de Vida Configurable**: Default 1.5 minutos según especificación
2. **Estados Explícitos**: FREE → ASSIGNED → DEAD con transiciones claras
3. **Validación de Capacidad**: Verificación de tiempo restante para tareas
4. **Tiempo de Espera**: 10 segundos de buffer para todas las asignaciones

### 🏠 Gestión de Colonia
1. **Recursos Limitados**: Stock de comida controla creación de hormigas
2. **Capacidad Máxima**: 100 hormigas simultáneas según requisitos
3. **Limpieza Automática**: Removal of dead ants during operations
4. **Modo de Emergencia**: Activación automática durante crisis

### 🔄 Manejo de Crisis y Emergencias
1. **Reasignación Automática**: Basada en prioridades y tiempo de espera
2. **Preservación de Alta Prioridad**: Defense nunca pierde hormigas
3. **Tiempo de Gracia**: Mínimo 10 segundos antes de reasignar
4. **Creación Forzada**: Durante emergencias si hay recursos

## Configuración Académica

**Configuración por Defecto (Requisitos):**
- Máximo de hormigas: **100** (configurable, requisito académico)
- Stock inicial de comida: **1000** unidades
- Tiempo de vida de hormigas: **1.5 minutos**
- Costo por hormiga: **10 unidades de comida**
- Ganancia por misión exitosa: **20 unidades de comida**
- Tiempo de espera: **10 segundos**
- Puerto del servidor: **8000**

## Desarrollo y Metodología

Este proyecto sigue **estrictamente** los principios TDD/BDD académicos:

### 🔴🟢🔄 Ciclo TDD Implementado
1. **Red**: Escribir test que falla para nueva funcionalidad
2. **Green**: Implementar código mínimo para pasar el test
3. **Refactor**: Mejorar el código manteniendo tests verdes
4. **Repeat**: Ciclo continuo para cada nueva característica

### 📋 BDD para Requisitos de Negocio
1. **Given-When-Then**: Escenarios en lenguaje natural
2. **Stakeholder Readable**: Especificaciones comprensibles para no-técnicos
3. **Living Documentation**: Los tests BDD documentan comportamiento esperado
4. **Acceptance Criteria**: Cada scenario valida criterios de aceptación

### 🏗️ Prácticas de Calidad Implementadas
- **Test First**: Todas las features desarrolladas con tests primero
- **Continuous Testing**: Tests deben pasar antes de cualquier commit
- **Mocking**: Subsistemas externos simulados apropiadamente
- **Error Handling**: Cobertura completa de casos de error
- **Documentation**: Código auto-documentado con tests como especificación

## Despliegue con Docker

### 🚀 Desarrollo Local
```bash
# Desarrollo con recarga automática
docker-compose up --build

# Solo el servicio principal
docker build -t queen-ant-api .
docker run -p 8000:8000 queen-ant-api
```

### 🏭 Producción con Nginx
```bash
# Despliegue completo con proxy reverso
docker-compose --profile production up -d
```

**Características de Producción:**
- Load balancing con nginx
- Health checks automáticos
- Reinicio automático de servicios
- Logs centralizados
- Configuración de proxy reverso

### 🔧 Variables de Entorno
```bash
# Configuración opcional via environment
export MAX_ANTS=150
export FOOD_STOCK=2000
export ANT_LIFESPAN_MINUTES=2.0
```

## Cumplimiento de Requisitos Académicos

### ✅ Requisitos Funcionales Mínimos
- **[R1] Crear hormigas bajo demanda**: ✅ Implementado con validación de capacidad
- **[R2] Capacidad máxima configurable**: ✅ Default 100, completamente configurable
- **[R3] Asignar por prioridad**: ✅ Defense(1) > Communication(2) > Collection(3)
- **[R4] Validación de subsistemas**: ✅ Solo subsistemas conocidos aceptados

### ✅ Requisitos de Calidad/Pruebas
- **[Q1] TDD para reglas de capacidad**: ✅ Tests unitarios comprehensive
- **[Q2] TDD para prioridades**: ✅ Tests de asignación y reasignación
- **[Q3] TDD para asignación**: ✅ Validación de todos los flujos
- **[Q4] Tests de creación válida/inválida**: ✅ Casos exitosos y de error
- **[Q5] Tests de rechazo por capacidad**: ✅ Límites respetados
- **[Q6] Tests de reasignación**: ✅ Emergencias y prioridades
- **[Q7] Cobertura ≥ 80%**: ✅ Cobertura comprehensive de funcionalidad

### ✅ Stretch Goals Implementados
- **[S1] Expiración de hormigas**: ✅ Time-to-live con muerte automática
- **[S2] Manejo de crisis**: ✅ Reasignación automática por prioridades
- **[S3] Robustez de API**: ✅ Validaciones extensas y manejo de errores

## Licencia Académica

Este proyecto es desarrollado con fines **exclusivamente académicos** para demostrar:
- Implementación de metodologías **TDD/BDD**
- Diseño de **APIs RESTful** robustas
- Gestión de **recursos limitados** y **prioridades**
- **Testing comprehensive** con cobertura completa
- **Arquitectura modular** de sistemas distribuidos

**Grupo 3**: Subsistema de Hormiga Reina
**Curso**: Calidad y Pruebas de Software
**Metodología**: Test-Driven Development + Behavior-Driven Development
