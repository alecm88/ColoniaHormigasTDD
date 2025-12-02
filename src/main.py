from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from src.colony import Colony
from src.models import (
    # Request models
    AntRequest, AntReturn, EmergencyRequest, MultipleAntsRequest,
    # Response models
    AntResponse, AntAssignmentResponse, AntReturnResponse, EmergencyAntResponse,
    MultipleAntsResponse, ComprehensiveColonyStatus, ColonyStatus, SubsystemsResponse,
    ConfigurationResponse, FoodResponse, CleanupResponse, RootResponse, ErrorResponse
)

# OpenAPI metadata
tags_metadata = [
    {
        "name": "🏠 Sistema",
        "description": "Información general del Subsistema de Hormiga Reina",
    },
    {
        "name": "🐜 Gestión de Hormigas",
        "description": "**Endpoints principales para requisitos académicos:**\n\n"
                      "- **R1**: Dar Hormiga - Asignación a subsistemas\n"
                      "- **R2**: Devolver Hormiga - Retorno con estado\n"
                      "- **R3**: Emergencia - Reasignación por prioridades",
    },
    {
        "name": "📊 Estado y Consultas",
        "description": "Endpoints para consultar el estado de la colonia y hormigas individuales",
    },
    {
        "name": "⚙️ Configuración",
        "description": "Administración de parámetros de la colonia: capacidad, comida, ciclo de vida",
    },
    {
        "name": "🔧 Utilidades",
        "description": "Herramientas de mantenimiento y información del sistema",
    }
]

app = FastAPI(
    title="🐜👑 Subsistema de Hormiga Reina",
    version="2.0.0",
    description="""
## 🎓 Proyecto Académico - Calidad y Pruebas de Software

**Sistema modular de simulación de colonia de hormigas implementado con TDD/BDD**

### 🏗️ Arquitectura del Subsistema
Este subsistema es responsable de la **gestión, asignación y control de hormigas**
para otros subsistemas del ecosistema de la colonia:

- **🛡️ Defense** (Prioridad 1) - Defensa de la colonia
- **📡 Communication** (Prioridad 2) - Gestión de mensajes
- **🌾 Collection** (Prioridad 3) - Recolección de recursos

### ✅ Requisitos Académicos Implementados
- **R1 - Dar Hormiga**: Asignación con validación de prioridades y recursos
- **R2 - Devolver Hormiga**: Retorno con estado (exitosa/muerta, con/sin comida)
- **R3 - Emergencia**: Reasignación automática basada en jerarquía de prioridades

### 🧪 Metodología TDD + BDD
- **68+ Tests Unitarios** con cobertura ≥ 80%
- **6 Scenarios BDD** validando comportamientos de negocio
- **Ciclo Red-Green-Refactor** aplicado consistentemente

### 🐜 Características de las Hormigas
- **Tiempo de vida**: 1.5 minutos (configurable)
- **Estados**: FREE → ASSIGNED → DEAD
- **Recursos**: 10 unidades comida/hormiga, +20 por misión exitosa
- **Capacidad**: Máximo 100 hormigas simultáneas (configurable)

### 🚀 Interfaces Disponibles
- **Swagger UI**: `/docs` - Interfaz interactiva para testing
- **ReDoc**: `/redoc` - Documentación detallada y exportable
- **OpenAPI JSON**: `/openapi.json` - Schema para generación de clientes
    """,
    openapi_tags=tags_metadata,
    contact={
        "name": "Grupo 3 - Subsistema Hormiga Reina",
        "email": "grupo3@universidad.edu",
    },
    license_info={
        "name": "Académico",
        "identifier": "Academic Use Only",
    },
    servers=[
        {
            "url": "https://coloniahormigastdd-production.up.railway.app",
            "description": "Servidor de producción en Railway"
        },
        {
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo"
        },
        {
            "url": "http://localhost",
            "description": "Servidor local alternativo"
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global colony instance - configuración según requisitos académicos
colony = Colony(max_ants=100, initial_food_stock=1000, ant_lifespan_minutes=1.5)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirige automáticamente a la documentación Swagger"""
    return RedirectResponse(url="/docs")


@app.get(
    "/info",
    response_model=RootResponse,
    tags=["🏠 Sistema"],
    summary="🏠 Información del Subsistema",
    description="""
    Endpoint informativo que devuelve datos básicos del **Subsistema de Hormiga Reina**.

    Útil para verificar:
    - ✅ Conectividad con la API
    - ✅ Versión del subsistema
    - ✅ Subsistemas externos disponibles
    - ✅ Estado general del servicio
    """
)
async def get_system_info():
    return {
        "message": "Queen Ant Subsystem - Ant Colony Management System",
        "version": "2.0.0",
        "subsystem": "Queen Ant (Hormiga Reina)",
        "available_subsystems": ["communication", "collection", "defense"]
    }


# === 🐜 ENDPOINTS PRINCIPALES PARA GESTIÓN DE HORMIGAS ===

@app.post(
    "/ants/request",
    response_model=AntAssignmentResponse,
    status_code=status.HTTP_200_OK,
    tags=["🐜 Gestión de Hormigas"],
    summary="🎯 R1: Solicitar Hormiga para Subsistema",
    description="""
    ## 📋 Requisito Académico R1: Dar Hormiga

    **Funcionalidad principal** para asignar hormigas a subsistemas solicitantes.

    ### 🔍 Validaciones Implementadas:
    - ✅ **Subsistema conocido**: Solo acepta Defense, Communication, Collection
    - ✅ **Recursos suficientes**: Verifica stock de comida y capacidad
    - ✅ **Vida restante**: La hormiga debe poder completar la tarea
    - ✅ **Prioridades**: Respeta jerarquía Defense > Communication > Collection

    ### 🏗️ Comportamiento:
    1. Busca hormiga libre con vida suficiente
    2. Si no encuentra, intenta crear nueva hormiga
    3. Si no puede crear, rechaza la solicitud
    4. Asigna hormiga al subsistema solicitante

    ### 📊 Códigos de Respuesta:
    - **200**: Asignación exitosa
    - **400**: Subsistema desconocido
    - **409**: Sin recursos/capacidad suficiente
    """,
    responses={
        200: {"description": "Hormiga asignada exitosamente", "model": AntAssignmentResponse},
        400: {"description": "Subsistema desconocido", "model": ErrorResponse},
        409: {"description": "Sin recursos o capacidad suficiente", "model": ErrorResponse},
    }
)
async def request_ant(request: AntRequest):
    """
    R1: Dar hormiga - Solicitar una hormiga para asignación a un subsistema
    Valida subsistema conocido, prioridad, y capacidad de la hormiga para la tarea
    """
    ant = colony.request_ant(
        subsystem_name=request.subsystem_name,
        priority=request.priority,
        estimated_duration_seconds=request.estimated_duration_seconds
    )

    if ant is None:
        # Determinar motivo del rechazo
        if request.subsystem_name.lower() not in ["communication", "collection", "defense"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown subsystem: {request.subsystem_name}. Valid options: communication, collection, defense"
            )

        status = colony.get_comprehensive_status()
        if status['food_stock'] < colony.food_per_ant:
            raise HTTPException(
                status_code=409,
                detail="Insufficient food stock to create new ants"
            )

        if not status['can_create_more']:
            raise HTTPException(
                status_code=409,
                detail="No available ants and cannot create more (capacity reached)"
            )

        raise HTTPException(
            status_code=409,
            detail="No ants available with sufficient remaining life for this task"
        )

    return {
        "message": f"Ant assigned to {request.subsystem_name}",
        "ant": ant.to_dict(),
        "assignment_successful": True
    }


@app.post(
    "/ants/request-multiple",
    response_model=MultipleAntsResponse,
    status_code=200,
    summary="📦 Solicitar múltiples hormigas (Operación en bloque)",
    description="""
    ## 🎯 Propósito
    Solicita múltiples hormigas de una vez para asignación a un subsistema específico.

    ## ⚡ Características principales

    ### Operación Atómica
    - ✅ **Todo o nada**: Se asignan TODAS las hormigas solicitadas o NINGUNA
    - 🔄 **Rollback automático**: Si falla parcialmente, revierte cualquier asignación

    ### Estrategia de Asignación
    1. **Prioridad a existentes**: Usa primero hormigas disponibles en la colonia
    2. **Creación inteligente**: Crea nuevas hormigas solo si es necesario
    3. **Validación de recursos**: Verifica capacidad y stock de comida antes de proceder

    ## 📊 Información de Respuesta

    La respuesta incluye información detallada sobre:
    - `success`: Indica si la operación fue exitosa
    - `ants`: Lista de hormigas asignadas (vacía si falla)
    - `ants_used`: Cuántas hormigas existentes se utilizaron
    - `ants_created`: Cuántas nuevas hormigas se crearon
    - `available`: Hormigas disponibles antes de la solicitud
    - `can_create`: Máximo de hormigas que se podían crear
    - `message`: Descripción detallada del resultado

    ## 🚨 Casos de Fallo

    La operación falla (sin asignar ninguna hormiga) cuando:
    - No hay suficientes hormigas disponibles + creables
    - El subsistema especificado no existe
    - La cantidad solicitada es inválida (≤ 0)
    - **⏰ Duración excesiva**: La duración estimada supera la vida útil de las hormigas (por defecto: 90 segundos)

    ## ⚠️ Limitación Importante - Cálculo de Duración

    **Vida útil de hormigas**: Por defecto, las hormigas viven 90 segundos (1.5 minutos).

    ### 📐 Fórmula de Cálculo:
    ```
    estimated_duration_seconds + 10s_tiempo_espera ≤ 90s_vida_útil
    ```

    **Tiempo de espera fijo**: Cada hormiga requiere **10 segundos adicionales** de tiempo de espera.

    ### ✅ Ejemplos válidos:
    - `estimated_duration_seconds: 40` → 40s + 10s = 50s ≤ 90s ✅
    - `estimated_duration_seconds: 70` → 70s + 10s = 80s ≤ 90s ✅
    - `estimated_duration_seconds: 79` → 79s + 10s = 89s ≤ 90s ✅

    ### ❌ Ejemplos inválidos:
    - `estimated_duration_seconds: 80` → 80s + 10s = 90s ≥ 90s ❌ (margen muy estrecho)
    - `estimated_duration_seconds: 85` → 85s + 10s = 95s > 90s ❌

    **Recomendación**: Use máximo 79 segundos para tener margen de seguridad.

    Para tareas más largas, configure primero la colonia con `POST /colony/configure` aumentando `ant_lifespan_minutes`.

    ## 💡 Ejemplo de Uso

    ```python
    # Solicitar 5 hormigas para Defense
    response = requests.post('/ants/request-multiple', json={
        "subsystem_name": "Defense",
        "quantity": 5,
        "priority": 1,
        "estimated_duration_seconds": 70  # 70s + 10s espera = 80s < 90s vida útil
    })

    if response.json()['success']:
        print(f"Asignadas: {len(response.json()['ants'])}")
    ```

    ## 🔗 Endpoints Relacionados
    - `POST /ants/request`: Solicitar una sola hormiga
    - `POST /ants/emergency`: Solicitar hormigas de emergencia
    - `GET /colony/status/comprehensive`: Ver estado de la colonia
    """,
    tags=["🐜 Gestión de Hormigas"],
    responses={
        200: {
            "description": "Operación completada (exitosa o fallida)",
            "model": MultipleAntsResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "✅ Solicitud exitosa",
                            "value": {
                                "success": True,
                                "message": "Successfully assigned 5 ants",
                                "ants": [
                                    {
                                        "id": "ant-123",
                                        "state": "assigned",
                                        "assigned_to": "defense",
                                        "remaining_life_seconds": 89.2,
                                        "estimated_duration_seconds": 80
                                    }
                                ],
                                "ants_used": 2,
                                "ants_created": 3,
                                "available": 2,
                                "can_create": 10,
                                "requested": 5
                            }
                        },
                        "failure": {
                            "summary": "❌ Recursos insuficientes",
                            "value": {
                                "success": False,
                                "message": "Cannot fulfill request for 10 ants. Available: 3, Can create: 2",
                                "ants": [],
                                "ants_used": 0,
                                "ants_created": 0,
                                "available": 3,
                                "can_create": 2,
                                "requested": 10
                            }
                        }
                    }
                }
            }
        }
    }
)
async def request_multiple_ants(request: MultipleAntsRequest):
    """
    Solicitar múltiples hormigas de forma atómica

    Si la solicitud no puede ser completada en su totalidad, no se asigna ninguna hormiga.
    """
    result = colony.request_ants(
        subsystem_name=request.subsystem_name,
        quantity=request.quantity,
        priority=request.priority,
        estimated_duration_seconds=request.estimated_duration_seconds
    )

    # Convertir las hormigas a formato de respuesta
    ants_response = []
    for ant in result['ants']:
        ants_response.append(AntResponse(
            id=ant.id,
            birth_time=ant.birth_time.isoformat(),
            death_time=ant.death_time.isoformat(),
            is_alive=ant.is_alive,
            age_seconds=ant.age_seconds,
            remaining_life_seconds=ant.remaining_life_seconds,
            state=ant.state.value,
            assigned_to=ant.assigned_to.value if ant.assigned_to else None,
            assignment_time=ant.assignment_time.isoformat() if ant.assignment_time else None,
            wait_time_seconds=ant.wait_time_seconds
        ))

    return MultipleAntsResponse(
        success=result['success'],
        message=result['message'],
        ants=ants_response,
        ants_used=result['ants_used'],
        ants_created=result['ants_created'],
        available=result['available'],
        can_create=result['can_create'],
        requested=result['requested']
    )


@app.post(
    "/ants/return",
    response_model=AntReturnResponse,
    status_code=status.HTTP_200_OK,
    tags=["🐜 Gestión de Hormigas"],
    summary="🔄 R2: Devolver Hormiga de Misión",
    description="""
    ## 📋 Requisito Académico R2: Devolver Hormiga

    **Endpoint para el retorno** de hormigas que completaron (o no) sus misiones asignadas.

    ### 🎯 Casos de Uso:
    - ✅ **Misión exitosa**: Hormiga regresa sana, posiblemente con comida
    - ✅ **Misión exitosa con comida**: +20 unidades al stock de la colonia
    - ❌ **Muerte en misión**: Hormiga marcada como muerta
    - 🔄 **Reasignación**: Hormiga libre queda disponible para nuevas misiones

    ### 🏗️ Comportamiento:
    1. Localiza la hormiga por ID
    2. Si regresa con comida, incrementa stock (+20 unidades)
    3. Si murió, marca como DEAD
    4. Si sobrevivió, marca como FREE
    5. Limpia asignación y tiempo de asignación

    ### 📊 Códigos de Respuesta:
    - **200**: Retorno procesado exitosamente
    - **404**: Hormiga no encontrada
    """,
    responses={
        200: {"description": "Retorno procesado exitosamente", "model": AntReturnResponse},
        404: {"description": "Hormiga no encontrada", "model": ErrorResponse},
    }
)
async def return_ant(return_data: AntReturn):
    success = colony.return_ant(
        ant_id=return_data.ant_id,
        returned_with_food=return_data.returned_with_food,
        died_in_mission=return_data.died_in_mission
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ant with ID {return_data.ant_id} not found"
        )

    status_msg = "returned"
    if return_data.died_in_mission:
        status_msg = "died in mission"
    elif return_data.returned_with_food:
        status_msg = "returned with food"

    return {
        "message": f"Ant {return_data.ant_id} {status_msg}",
        "food_gained": return_data.returned_with_food and not return_data.died_in_mission,
        "ant_died": return_data.died_in_mission
    }


@app.post(
    "/ants/emergency",
    response_model=List[EmergencyAntResponse],
    status_code=status.HTTP_200_OK,
    tags=["🐜 Gestión de Hormigas"],
    summary="🚨 R3: Solicitar Hormigas de Emergencia",
    description="""
    ## 📋 Requisito Académico R3: Emergencia y Reasignación

    **Endpoint crítico** para manejo de crisis que requieren reasignación de hormigas basada en prioridades.

    ### 🎯 Jerarquía de Prioridades (Reasignación):
    - **🛡️ Defense (1)** puede tomar hormigas de Communication y Collection
    - **📡 Communication (2)** puede tomar hormigas de Collection
    - **🌾 Collection (3)** no puede tomar hormigas de otros subsistemas

    ### 🏗️ Algoritmo de Emergencia:
    1. **Paso 1**: Busca hormigas libres disponibles
    2. **Paso 2**: Si insuficientes, identifica hormigas reasignables:
       - Solo de subsistemas con menor prioridad
       - Que hayan esperado al menos `max_wait_seconds`
    3. **Paso 3**: Reasigna hormigas al subsistema solicitante
    4. **Paso 4**: Activa modo emergencia en la colonia

    ### ⏰ Tiempo de Gracia:
    - Mínimo **10 segundos** de espera antes de reasignar
    - Configurable con parámetro `max_wait_seconds`

    ### 📊 Respuesta:
    Retorna lista de hormigas asignadas con metadatos de reasignación
    """,
    responses={
        200: {"description": "Hormigas de emergencia asignadas", "model": List[EmergencyAntResponse]},
    }
)
async def request_emergency_ants(request: EmergencyRequest):
    emergency_ants = colony.request_emergency_ants(
        requesting_subsystem=request.requesting_subsystem,
        number_needed=request.number_needed,
        max_wait_seconds=request.max_wait_seconds
    )

    return [
        {
            "ant": ant.to_dict(),
            "reassigned": True,
            "emergency_assignment": True
        }
        for ant in emergency_ants
    ]


# === 📊 ENDPOINTS DE CONSULTA Y ESTADO ===

@app.get(
    "/colony/status/comprehensive",
    response_model=ComprehensiveColonyStatus,
    tags=["📊 Estado y Consultas"],
    summary="📈 Estado Detallado del Hormiguero",
    description="""
    **Endpoint principal** para consultar el estado comprehensive de la colonia.

    ### 📊 Información Incluida:
    - 🐜 **Estadísticas de hormigas**: totales, vivas, libres, asignadas, muertas
    - 🍯 **Recursos**: stock actual de comida y capacidad de creación
    - 🏗️ **Capacidad**: máximo configurado y disponibilidad
    - 🚨 **Estado operacional**: modo emergencia, distribución por subsistema
    - ⏰ **Configuración**: tiempo de vida de hormigas

    **Ideal para dashboards y monitoreo** del estado general del subsistema.
    """
)
async def get_comprehensive_colony_status():
    return colony.get_comprehensive_status()


@app.get(
    "/ants",
    response_model=List[AntResponse],
    tags=["📊 Estado y Consultas"],
    summary="📋 Consultar Hormigas con Filtros",
    description="""
    Consulta hormigas en la colonia con **filtros opcionales** por estado.

    ### 🔍 Filtros Disponibles:
    - **`state=free`**: Solo hormigas libres (disponibles para asignación)
    - **`state=assigned`**: Solo hormigas asignadas a subsistemas
    - **`state=dead`**: Solo hormigas muertas
    - **Sin filtro**: Todas las hormigas vivas (free + assigned)

    ### 📊 Casos de Uso:
    - **Monitoreo**: Ver hormigas disponibles antes de solicitar asignación
    - **Debug**: Investigar estado de hormigas específicas
    - **Análisis**: Estadísticas de uso por subsistema
    """
)
async def get_all_ants(
    state: str = Query(
        None,
        description="Filtrar por estado",
        regex="^(free|assigned|dead)$",
        examples=["free", "assigned", "dead"]
    )
):
    colony.update_all_ant_states()

    if state == "free":
        ants = colony.get_free_ants()
    elif state == "assigned":
        ants = colony.get_assigned_ants()
    elif state == "dead":
        ants = [ant for ant in colony.ants.values() if not ant.is_alive]
    else:
        ants = colony.get_alive_ants()

    return [ant.to_dict() for ant in ants]


@app.get(
    "/ants/{ant_id}",
    response_model=AntResponse,
    tags=["📊 Estado y Consultas"],
    summary="🔍 Consultar Hormiga Específica",
    description="""
    Obtener **información detallada** de una hormiga específica por su ID único.

    ### 📋 Información Retornada:
    - 🆔 **Identificación**: ID único y tiempo de nacimiento
    - ⏰ **Ciclo de vida**: edad actual, tiempo restante, muerte estimada
    - 📊 **Estado actual**: FREE/ASSIGNED/DEAD
    - 🎯 **Asignación**: subsistema asignado y tiempo de asignación (si aplica)

    **Útil para tracking** de hormigas específicas durante operaciones.
    """,
    responses={
        200: {"description": "Información de la hormiga", "model": AntResponse},
        404: {"description": "Hormiga no encontrada", "model": ErrorResponse},
    }
)
async def get_ant(ant_id: str):
    ant = colony.ants.get(ant_id)
    if ant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ant not found"
        )

    # Update state before returning
    ant.update_state()
    return ant.to_dict()


# === ⚙️ ENDPOINTS DE CONFIGURACIÓN Y ADMINISTRACIÓN ===

@app.post(
    "/ants",
    response_model=AntResponse,
    tags=["⚙️ Configuración"],
    summary="🧪 Crear Hormiga Directamente",
    description="""
    **Endpoint de administración** para crear una hormiga directamente sin asignación.

    ⚠️ **Solo para testing y propósitos administrativos**

    ### 🏗️ Comportamiento:
    - Crea una hormiga en estado FREE
    - Consume 10 unidades de comida del stock
    - Valida recursos y capacidad disponible
    - Útil para testing de otros endpoints

    ### 📊 Validaciones:
    - Stock de comida suficiente (≥10 unidades)
    - Capacidad de colonia no excedida
    """,
    responses={
        200: {"description": "Hormiga creada exitosamente", "model": AntResponse},
        409: {"description": "Sin recursos o capacidad suficiente", "model": ErrorResponse},
    }
)
async def create_ant_directly():
    ant = colony.create_ant()
    if ant is None:
        status = colony.get_comprehensive_status()
        if status['food_stock'] < colony.food_per_ant:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot create ant: insufficient food stock"
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot create ant: colony is at maximum capacity"
        )
    return ant.to_dict()


@app.put(
    "/colony/config",
    response_model=ConfigurationResponse,
    tags=["⚙️ Configuración"],
    summary="⚙️ Configurar Parámetros de la Colonia",
    description="""
    **Endpoint de administración** para modificar parámetros operacionales de la colonia.

    ### 🔧 Parámetros Configurables:
    - **`max_ants`**: Capacidad máxima de hormigas simultáneas
    - **`food_stock`**: Stock actual de comida disponible
    - **`ant_lifespan_minutes`**: Tiempo de vida de nuevas hormigas

    ### 📊 Validaciones:
    - `max_ants` ≥ 1
    - `food_stock` ≥ 0
    - `ant_lifespan_minutes` > 0

    ### 🎯 Casos de Uso:
    - **Ajuste de capacidad** según demanda de subsistemas
    - **Gestión de recursos** para balancear creación/consumo
    - **Testing** con diferentes configuraciones de ciclo de vida
    """,
    responses={
        200: {"description": "Configuración actualizada", "model": ConfigurationResponse},
        400: {"description": "Parámetros inválidos", "model": ErrorResponse},
    }
)
async def configure_colony(
    max_ants: int = Query(None, description="Capacidad máxima de hormigas", ge=1, examples=[100, 150, 200]),
    food_stock: int = Query(None, description="Stock actual de comida", ge=0, examples=[1000, 500, 2000]),
    ant_lifespan_minutes: float = Query(None, description="Tiempo de vida en minutos", gt=0, examples=[1.5, 2.0, 3.0])
):
    config_changes = {}

    if max_ants is not None:
        if max_ants < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="max_ants must be at least 1")
        colony.max_ants = max_ants
        config_changes["max_ants"] = max_ants

    if food_stock is not None:
        if food_stock < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="food_stock cannot be negative")
        colony.food_stock = food_stock
        config_changes["food_stock"] = food_stock

    if ant_lifespan_minutes is not None:
        if ant_lifespan_minutes <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ant_lifespan_minutes must be positive")
        colony.ant_lifespan_minutes = ant_lifespan_minutes
        config_changes["ant_lifespan_minutes"] = ant_lifespan_minutes

    return {
        "message": "Colony configuration updated",
        "changes": config_changes,
        "current_status": colony.get_comprehensive_status()
    }


@app.post(
    "/colony/food/add",
    response_model=FoodResponse,
    tags=["⚙️ Configuración"],
    summary="🍯 Agregar Comida al Stock",
    description="""
    **Simula misiones exitosas** de recolección agregando comida al stock de la colonia.

    ### 🎯 Funcionalidad:
    - Incrementa el stock de comida disponible
    - Permite creación de más hormigas
    - Simula retorno exitoso de misiones de Collection

    ### 📊 Uso Típico:
    - **Testing**: Asegurar recursos para crear hormigas
    - **Simulación**: Modelar ciclos de recolección exitosos
    - **Recovery**: Recuperar stock después de muchas creaciones
    """,
    responses={
        200: {"description": "Comida agregada exitosamente", "model": FoodResponse},
        400: {"description": "Cantidad inválida", "model": ErrorResponse},
    }
)
async def add_food(
    amount: int = Query(..., description="Cantidad de comida a agregar", gt=0, examples=[50, 100, 200])
):
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")

    colony.add_food(amount)
    return {
        "message": f"Added {amount} food units",
        "total_food_stock": colony.food_stock
    }


# === 🔧 ENDPOINTS DE UTILIDADES ===

@app.post(
    "/colony/cleanup",
    response_model=CleanupResponse,
    tags=["🔧 Utilidades"],
    summary="🧹 Limpiar Hormigas Muertas",
    description="""
    **Trigger manual** para limpieza de hormigas que han muerto por tiempo de vida agotado.

    ### 🏗️ Funcionalidad:
    - Remueve hormigas muertas de la colonia
    - Libera espacio para crear nuevas hormigas
    - Normalmente se ejecuta automáticamente, pero puede hacerse manual

    ### 📊 Respuesta:
    - Número de hormigas limpiadas
    - Hormigas vivas restantes después de limpieza

    **Útil para mantenimiento** y liberación de recursos.
    """
)
async def cleanup_dead_ants():
    cleaned_count = colony.cleanup_dead_ants()
    return {
        "message": f"Cleaned up {cleaned_count} dead ants",
        "remaining_ants": len(colony.get_alive_ants())
    }


@app.get(
    "/colony/status",
    response_model=ColonyStatus,
    tags=["🔧 Utilidades"],
    summary="📊 Estado Básico (Compatibilidad)",
    description="""
    **Endpoint de compatibilidad** que retorna estado básico de la colonia.

    Mantiene **retrocompatibilidad** con versiones anteriores del API.
    Para información detallada, usar `/colony/status/comprehensive`.
    """
)
async def get_basic_colony_status():
    return colony.get_status()


@app.get(
    "/subsystems",
    response_model=SubsystemsResponse,
    tags=["🔧 Utilidades"],
    summary="🏗️ Información de Subsistemas",
    description="""
    **Información de referencia** sobre los subsistemas disponibles y sus prioridades.

    ### 📋 Información Incluida:
    - **IDs y nombres** de subsistemas disponibles
    - **Niveles de prioridad** (1=máxima, 3=mínima)
    - **Explicación** de jerarquía para reasignaciones

    ### 🎯 Jerarquía de Prioridades:
    1. **🛡️ Defense**: Máxima prioridad, puede tomar hormigas de otros
    2. **📡 Communication**: Prioridad media, puede tomar de Collection
    3. **🌾 Collection**: Mínima prioridad, no puede tomar de otros

    **Referencia esencial** para entender el sistema de prioridades.
    """
)
async def get_available_subsystems():
    from src.subsystems import Subsystem
    subsystems = Subsystem.get_known_subsystems()

    return {
        "available_subsystems": [
            {
                "id": subsystem.id.value,
                "name": subsystem.name,
                "priority_level": subsystem.priority_level
            }
            for subsystem in subsystems.values()
        ],
        "priority_explanation": {
            "1": "Highest priority (Defense)",
            "2": "Medium priority (Communication)",
            "3": "Lowest priority (Collection)"
        }
    }