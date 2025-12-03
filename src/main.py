from fastapi import FastAPI, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import (
    request_validation_exception_handler
)
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from src.colony import Colony
from src.service import Service
from src.subsystems import Subsystem, SubsystemType
from src.models import (
    # Request models
    AntRequest, AntReturn, EmergencyRequest, MultipleAntsRequest,
    # Response models
    AntResponse, ContenidoResponse, AntAssignmentResponse, AntReturnResponse, EmergencyAntResponse,
    MultipleAntsResponse, ComprehensiveColonyStatus, ColonyStatus, SubsystemsResponse, MessageResponse,
    ConfigurationResponse, FoodResponse, CleanupResponse, RootResponse, ErrorResponse,
    ServiceResponse
)
import requests, time

# Global colony instance - configuración según requisitos académicos
colony = Colony(max_ants=100, initial_food_stock=20, ant_lifespan_minutes=1.5, food_per_ant=1)
# Global service instance in charge of message queue
globalService = Service(interval=5, run_for_minutes=0.1, colony=colony)

# OpenAPI metadata
tags_metadata = [
    {
        "name": "🏠 Sistema",
        "description": "Información general del Subsistema de Hormiga Reina",
    },
    {
        "name": "🐜 Gestión de Hormigas",
        "description": "**Endpoints principales para requisitos académicos:**\n\n"
                      "- **Servicio**: Integracion con comunicacion para manejo de cola de mensajes\n"
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

- **🛡️ Defensa** (Prioridad 1) - Defensa de la colonia
- **🌾 Recolección** (Prioridad 3) - Recolección de recursos

### ✅ Requisitos Académicos Implementados
- **Servicio**: Integracion con comunicacion para manejo de cola de mensajes
- **R1 - Dar Hormiga**: Asignación con validación de prioridades y recursos
- **R2 - Devolver Hormiga**: Retorno con estado (exitosa/muerta, con/sin comida)
- **R3 - Emergencia**: Reasignación automática basada en jerarquía de prioridades

### 🧪 Metodología TDD + BDD
- **130+ Tests Unitarios** con cobertura ≥ 90%
- **6 Scenarios BDD** validando comportamientos de negocio
- **Ciclo Red-Green-Refactor** aplicado consistentemente

### 🐜 Características de las Hormigas
- **Tiempo de vida**: 1.5 minutos (configurable)
- **Estados**: FREE → ASSIGNED → DEAD
- **Recursos**: 1 unidad comida/hormiga (configurable)
- **Capacidad**: Máximo 100 hormigas simultáneas (configurable)

### 🚀 Interfaces Disponibles
- **Swagger UI**: `/docs` - Interfaz interactiva para testing
- **ReDoc**: `/redoc` - Documentación detallada y exportable
- **OpenAPI JSON**: `/openapi.json` - Schema para generación de clientes
    """,
    openapi_tags=tags_metadata,
    contact={
        "name": "Grupo 3 - Subsistema Hormiga Reina"
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

# # === 📊 ENDPOINTS DE CONSULTA Y ESTADO ===

@app.get("/")
async def root():
    return {
        "message": "Sistema de Hormiga Reina"
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
        pattern="^(free|assigned|dead)$",
        examples=["free", "assigned", "dead"]
    )
):
    # colony.update_all_ant_states()

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
            detail="Hormiga no encontrada"
        )

    # Update state before returning
    # ant.update_state()
    return ant.to_dict()

@app.get(
    "/messages/{subsystem_id}",
    response_model=List[MessageResponse],
    tags=["📊 Estado y Consultas"],
    summary="🔍 Consultar Mensajes para un Subsistema",
    description="""
    Obtiene todos los mensajes activos (no expirados) dirigidos a un subsistema específico.

    """,
    responses={
        200: {"description": "Lista de mensajes activos(no expirados)", "model": List[MessageResponse]},
        404: {"description": "No hay mensajes activos para el subsistema", "model": ErrorResponse},
    }
)
async def get_messages(subsystem_id: str):
    comunicacionUrl = (f"https://communicationservice-production.up.railway.app/api/mensaje/{subsystem_id}")

    response = requests.get(comunicacionUrl)
    data = response.json() 
    
    return data


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
        "message": "Subsistema Hormiga Reina",
        "version": "1.0.0",
        "subsystem": "S03_REI",
        "available_subsystems": ["S01_COM", "S02_REC", "S04_ENT", "S05_DEF"]
    }


# # === 🐜 ENDPOINTS PRINCIPALES PARA GESTIÓN DE HORMIGAS ===

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
    - ✅ **Subsistema conocido**: Solo acepta Defense, Comunicacion, Recolección
    - ✅ **Recursos suficientes**: Verifica stock de comida y capacidad
    - ✅ **Vida restante**: La hormiga debe poder completar la tarea
    - ✅ **Prioridades**: Respeta jerarquía Defense > Comunicacion > Recolección

    ### 🏗️ Comportamiento:
    1. Busca hormiga libre con vida suficiente
    2. Si no encuentra, intenta crear nueva hormiga
    3. Si no puede crear, rechaza la solicitud
    4. Asigna hormiga al subsistema solicitante

    ### 📊 Códigos de Respuesta:
    - **200**: Asignación exitosa
    - **400**: Subsistema desconocido
    - **409**: Sin recursos/capacidad suficiente
    - **422**: Bad payload/Subsistema invalido
    """,
    responses={
        200: {"description": "Hormiga asignada exitosamente", "model": AntAssignmentResponse},
        400: {"description": "Subsistema desconocido", "model": ErrorResponse},
        409: {"description": "Sin recursos o capacidad suficiente", "model": ErrorResponse},
        422: {"description": "Error en el formato o el subsistema no existe", "model": ErrorResponse},
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
        if  Subsystem.get_by_name(request.subsystem_name) is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown subsystem: {request.subsystem_name}."
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

    message = {
        "emisor": "S03_REI",
        "receptor": f"{request.subsystem_name.value}",
        "mensaje": {
            "message": f"Ant assigned to {request.subsystem_name}",
            "ant": ant.to_dict(),
            "assignment_successful": True
        }
    }

    comunicacionUrl = "https://communicationservice-production.up.railway.app/api/mensaje"

    response = requests.post(comunicacionUrl, json=message)

    return response.json()

    # return {
    #     "emisor": "S03_REI",
    #     "receptor": f"{request.subsystem_name.value}",
    #     "mensaje": {
    #         "message": f"Ant assigned to {request.subsystem_name}",
    #         "ant": ant.to_dict(),
    #         "assignment_successful": True
    #     }
    # }


# @app.post(
#     "/ants/request",
#     response_model=AntAssignmentResponse,
#     status_code=status.HTTP_200_OK,
#     tags=["🐜 Gestión de Hormigas"],
#     summary="🎯 R1: Solicitar Hormiga para Subsistema",
#     description="""
#     ## 📋 Requisito Académico R1: Dar Hormiga

#     **Funcionalidad principal** para asignar hormigas a subsistemas solicitantes.

#     ### 🔍 Validaciones Implementadas:
#     - ✅ **Subsistema conocido**: Solo acepta Defense, Communication, Collection
#     - ✅ **Recursos suficientes**: Verifica stock de comida y capacidad
#     - ✅ **Vida restante**: La hormiga debe poder completar la tarea
#     - ✅ **Prioridades**: Respeta jerarquía Defense > Communication > Collection

#     ### 🏗️ Comportamiento:
#     1. Busca hormiga libre con vida suficiente
#     2. Si no encuentra, intenta crear nueva hormiga
#     3. Si no puede crear, rechaza la solicitud
#     4. Asigna hormiga al subsistema solicitante

#     ### 📊 Códigos de Respuesta:
#     - **200**: Asignación exitosa
#     - **400**: Subsistema desconocido
#     - **409**: Sin recursos/capacidad suficiente
#     """,
#     responses={
#         200: {"description": "Hormiga asignada exitosamente", "model": AntAssignmentResponse},
#         400: {"description": "Subsistema desconocido", "model": ErrorResponse},
#         409: {"description": "Sin recursos o capacidad suficiente", "model": ErrorResponse},
#     }
# )
# async def request_ant(request: AntRequest):
#     """
#     R1: Dar hormiga - Solicitar una hormiga para asignación a un subsistema
#     Valida subsistema conocido, prioridad, y capacidad de la hormiga para la tarea
#     """

#     ant = colony.request_ant(
#         subsystem_name=request.subsystem_name,
#         priority=request.priority,
#         estimated_duration_seconds=request.estimated_duration_seconds
#     )

#     if ant is None:
#         # Determinar motivo del rechazo
#         if request.subsystem_name.lower() not in ["communication", "collection", "defense"]:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Unknown subsystem: {request.subsystem_name}. Valid options: communication, collection, defense"
#             )

#         status = colony.get_comprehensive_status()
#         if status['food_stock'] < colony.food_per_ant:
#             raise HTTPException(
#                 status_code=409,
#                 detail="Insufficient food stock to create new ants"
#             )

#         if not status['can_create_more']:
#             raise HTTPException(
#                 status_code=409,
#                 detail="No available ants and cannot create more (capacity reached)"
#             )

#         raise HTTPException(
#             status_code=409,
#             detail="No ants available with sufficient remaining life for this task"
#         )

#     return {
#         "message": f"Ant assigned to {request.subsystem_name}",
#         "ant": ant.to_dict(),
#         "assignment_successful": True
#     }


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
        ants_response.append(
            ant.to_dict()
        )

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
    - ✅ **Misión exitosa con comida**: Se agregan las unidades de comida al stock de la colonia
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
    - **🛡️ Defense (1)** puede tomar hormigas de Comunicacion y Recolección
    - **🌾 Recolección (3)** no puede tomar hormigas de otros subsistemas

    ### 🏗️ Algoritmo de Emergencia:
    1. **Paso 1**: Busca hormigas libres disponibles
    2. **Paso 2**: Si insuficientes, identifica hormigas reasignables:
       - Solo de subsistemas con menor prioridad
    3. **Paso 3**: Reasigna hormigas al subsistema solicitante
    4. **Paso 4**: Activa modo emergencia en la colonia

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
        number_needed=request.number_needed
    )

    return [
        {
            "ant": ant.to_dict(),
            "reassigned": True,
            "emergency_assignment": True
        }
        for ant in emergency_ants
    ]


# # === ⚙️ ENDPOINTS DE CONFIGURACIÓN Y ADMINISTRACIÓN ===

@app.post(
    "/service",
    response_model=ServiceResponse,
    tags=["⚙️ Servicio"],
    summary="⚙️ Levantar servicio",
    description="""
    **Endpoint de administración** para modificar parámetros operacionales de la colonia.
    """,
    responses={
        200: {"description": "Servicio actualizado", "model": ServiceResponse},
        400: {"description": "Parámetros inválidos", "model": ErrorResponse},
    }
)
async def service(
    interval: int = Query(1, description="Cada cuantos segundos se corre la consulta", ge=1, examples=[1, 10, 20]),
    run_for_minutes: float = Query(5, description="Numero de minutos para mantener vivo el servicio", ge=0.1, examples=[5, 10, 20]),
    activate: bool = Query(None, description="Inicio del servicio", examples=[True, False])
):
    config_changes = {}

    if interval is not None:
        if interval < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="interval must be at least 1")
        globalService.interval = interval
        config_changes["interval"] = interval

    if run_for_minutes is not None:
        if run_for_minutes < 0.1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="run_for_minutes must be at least 0.1")
        config_changes["run_for_minutes"] = run_for_minutes
        globalService.run_for_minutes = run_for_minutes

    if activate is not None:
        if (activate):
            globalService.service_start()
        else:
            globalService.service_stop()
        config_changes['Service start'] = activate

    time.sleep(1)  # Give some time for service to update

    return {
        "message": "Service configuration updated",
        "changes": config_changes,
        "current_status": globalService.get_status()
    }


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
    - Consume 1 unidades de comida del stock (variable de la colonia)
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
        status_colonia = colony.get_comprehensive_status()
        if status_colonia['food_stock'] < colony.food_per_ant:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Sin recursos"
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sin capacidad"
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
    - **`food_per_ant`**: Comida consumida por hormiga
    - **`ant_lifespan_minutes`**: Tiempo de vida de nuevas hormigas

    ### 📊 Validaciones:
    - `max_ants` ≥ 1
    - `food_stock` ≥ 0
    - `food_per_ant` ≥ 1
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
    food_per_ant: int = Query(None, description="Comida consumida por hormiga", ge=1, examples=[1, 20, 30]),
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

    if food_per_ant is not None:
        if food_per_ant < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="food_per_ant must be at least 1")
        colony.food_per_ant = food_per_ant
        config_changes["food_per_ant"] = food_per_ant

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


@app.put(
    "/colony/emergency",
    response_model=ConfigurationResponse,
    tags=["⚙️ Configuración"],
    summary="⚙️ Configurar Parámetros de la Colonia",
    description="""
    **Endpoint de administración** para activar modo de emergencia.
    """,
    responses={
        200: {"description": "Configuración actualizada", "model": ConfigurationResponse},
        400: {"description": "Parámetros inválidos", "model": ErrorResponse},
    }
)
async def configure_colony(
    activate: bool = Query(None, description="Capacidad máxima de hormigas", examples=[True, False])
):
    config_changes = {}
    if (activate):
        colony.activate_emergency_mode()
    else:
        colony.deactivate_emergency_mode()
    config_changes['emergency_mode'] = activate

    return {
        "message": "Colony configuration updated",
        "changes": config_changes,
        "current_status": colony.get_comprehensive_status()
    }


# # === 🔧 ENDPOINTS DE UTILIDADES ===

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