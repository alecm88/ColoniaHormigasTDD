from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class AntStateEnum(str, Enum):
    """Estado de una hormiga en el sistema"""
    FREE = "free"
    ASSIGNED = "assigned"
    DEAD = "dead"
    
class SubsystemEnum(str, Enum):
    """Subsistemas disponibles en la colonia"""
    COMMUNICATION = "S01_COM"
    COLLECTION = "S02_REC"
    QUEEN = "S03_REI"
    HABITAT = "S04_ENT" #Environment could be reserved keyword
    DEFENSE = "S05_DEF"


# === REQUEST MODELS ===

class AntRequest(BaseModel):
    """
    Modelo para solicitar una hormiga a un subsistema.

    R1: Dar Hormiga - Endpoint principal para asignación de hormigas
    """
    subsystem_name: SubsystemEnum = Field(
        ...,
        description="Nombre del subsistema solicitante",
        examples=["Defense", "Communication", "Collection"]
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Prioridad de la solicitud (1=máxima, 3=mínima)"
    )
    estimated_duration_seconds: float = Field(
        default=60,
        gt=0,
        description="Duración estimada de la tarea en segundos"
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "subsystem_name": "Defense",
                "priority": 1,
                "estimated_duration_seconds": 120
            }
        }


class AntReturn(BaseModel):
    """
    Modelo para devolver una hormiga de una asignación.

    R2: Devolver Hormiga - Retorno con estado y posible comida
    """
    ant_id: str = Field(
        ...,
        description="ID único de la hormiga a devolver"
    )
    returned_with_food: bool = Field(
        default=False,
        description="Si la hormiga regresó con comida de la misión"
    )
    died_in_mission: bool = Field(
        default=False,
        description="Si la hormiga murió durante la misión"
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "ant_id": "550e8400-e29b-41d4-a716-446655440000",
                "returned_with_food": True,
                "died_in_mission": False
            }
        }


class EmergencyRequest(BaseModel):
    """
    Modelo para solicitar hormigas de emergencia.

    R3: Emergencia - Reasignación basada en prioridades durante crisis
    """
    requesting_subsystem: SubsystemEnum = Field(
        ...,
        description="Subsistema que solicita hormigas de emergencia"
    )
    number_needed: int = Field(
        ...,
        gt=0,
        description="Número de hormigas necesarias"
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "requesting_subsystem": "S05_DEF",
                "number_needed": 3
            }
        }


# === RESPONSE MODELS ===

class AntResponse(BaseModel):
    """Modelo completo de respuesta para una hormiga"""
    id: str = Field(description="ID único de la hormiga")
    birth_time: str = Field(description="Tiempo de nacimiento (ISO format)")
    death_time: str = Field(description="Tiempo estimado de muerte (ISO format)")
    is_alive: bool = Field(description="Si la hormiga está viva")
    age_seconds: float = Field(description="Edad actual en segundos")
    remaining_life_seconds: float = Field(description="Tiempo de vida restante en segundos")
    state: AntStateEnum = Field(description="Estado actual de la hormiga")
    assigned_to: Optional[SubsystemEnum] = Field(description="Subsistema asignado (si aplica)")
    assignment_time: Optional[str] = Field(description="Tiempo de asignación (ISO format)")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "birth_time": "2024-01-15T10:30:00.000000",
                "death_time": "2024-01-15T10:31:30.000000",
                "is_alive": True,
                "age_seconds": 15.5,
                "remaining_life_seconds": 74.5,
                "state": "assigned",
                "assigned_to": "defense",
                "assignment_time": "2024-01-15T10:30:15.500000"
            }
        }

class MessageResponse(BaseModel):
    """Formato de mensajes de Comunicacion"""
    id: str = Field(description="id de parte de comunicacion")
    timestamp: str = Field(description="fecha y hora recibida")
    emisor: str = Field(description="Subsistema emisor (S03_REI)")
    receptor: str = Field(description="Subsistema receptor")
    mensaje: dict = Field(description="Contenido del mensaje")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "id":"f71860a5-a0ea-40c8-ab6e-ec0b94209139",
                "emisor": "S03_REI",
                "receptor": "S05_DEF",
                "timestamp":"2025-11-22T20:44:10.039359218Z",
                "mensaje": {
                    "message": "Ant assigned to Defense",
                    "assignment_successful": True,
                    "ant": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "state": "assigned",
                        "assigned_to": "defense"
                    }
                }
            }
        }

# class CommunicationResponse(BaseModel):
#     """Respuesta de comunicacion al recibir mensajes"""
#     mensajes: Dict[int, MessageResponse] = Field(description="Lista de mensajes")

#     class ConfigDict:
#         json_schema_extra = {
#             "example": [
#                 {
#                     "id":"f71860a5-a0ea-40c8-ab6e-ec0b94209139",
#                     "emisor": "S03_REI",
#                     "receptor": "S05_DEF",
#                     "timestamp":"2025-11-22T20:44:10.039359218Z",
#                     "mensaje": {
#                         "message": "Ant assigned to Defense",
#                         "assignment_successful": True,
#                         "ant": {
#                             "id": "550e8400-e29b-41d4-a716-446655440000",
#                             "state": "assigned",
#                             "assigned_to": "defense"
#                         }
#                     }
#                 }
#             ]
#         }

class ContenidoResponse(BaseModel):
    message: str = Field(description="Mensaje de confirmación")
    assignment_successful: bool = Field(description="Si la asignación fue exitosa")
    ant: AntResponse = Field(description="Información de la hormiga asignada")

class AntAssignmentResponse(BaseModel):
    """Respuesta para asignación exitosa de hormiga"""
    id: str = Field(description="id de parte de comunicacion")
    timestamp: str = Field(description="fecha y hora recibida")
    emisor: str = Field(description="Subsistema emisor (S03_REI)")
    receptor: str = Field(description="Subsistema receptor")
    mensaje: ContenidoResponse = Field(description="Información de la hormiga asignada")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "id":"f71860a5-a0ea-40c8-ab6e-ec0b94209139",
                "emisor": "S03_REI",
                "receptor": "S05_DEF",
                "timestamp":"2025-11-22T20:44:10.039359218Z",
                "mensaje": {
                    "message": "Ant assigned to Defense",
                    "assignment_successful": True,
                    "ant": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "state": "assigned",
                        "assigned_to": "defense"
                    }
                }
            }
        }


# Esta clase utilizaba los sistema antiguos.
# class AntAssignmentResponse(BaseModel):
#     """Respuesta para asignación exitosa de hormiga"""
#     message: str = Field(description="Mensaje de confirmación")
#     assignment_successful: bool = Field(description="Si la asignación fue exitosa")
#     ant: AntResponse = Field(description="Información de la hormiga asignada")

#     class ConfigDict:
#         json_schema_extra = {
#             "example": {
#                 "message": "Ant assigned to Defense",
#                 "assignment_successful": True,
#                 "ant": {
#                     "id": "550e8400-e29b-41d4-a716-446655440000",
#                     "state": "assigned",
#                     "assigned_to": "defense"
#                 }
#             }
#         }


class AntReturnResponse(BaseModel):
    """Respuesta para devolución de hormiga"""
    message: str = Field(description="Mensaje de confirmación")
    food_gained: bool = Field(description="Si se ganó comida de la misión")
    ant_died: bool = Field(description="Si la hormiga murió")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "message": "Ant 550e8400-e29b-41d4-a716-446655440000 returned with food",
                "food_gained": True,
                "ant_died": False
            }
        }


class EmergencyAntResponse(BaseModel):
    """Respuesta individual para hormiga de emergencia"""
    ant: AntResponse = Field(description="Información de la hormiga")
    reassigned: bool = Field(description="Si fue reasignada de otra tarea")
    emergency_assignment: bool = Field(description="Si es una asignación de emergencia")


class ColonyStatus(BaseModel):
    """Estado básico de la colonia (compatibilidad)"""
    total_ants: int = Field(description="Total de hormigas en la colonia")
    alive_ants: int = Field(description="Hormigas vivas")
    free_ants: int = Field(description="Hormigas libres (no asignadas)")
    assigned_ants: int = Field(description="Hormigas asignadas")
    dead_ants: int = Field(description="Hormigas muertas")
    max_ants: int = Field(description="Capacidad máxima de hormigas")
    food_stock: int = Field(description="Stock actual de comida")

class ComprehensiveColonyStatus(BaseModel):
    """Estado detallado de la colonia"""
    total_ants: int = Field(description="Total de hormigas en la colonia")
    alive_ants: int = Field(description="Hormigas vivas")
    free_ants: int = Field(description="Hormigas libres (no asignadas)")
    assigned_ants: int = Field(description="Hormigas asignadas")
    dead_ants: int = Field(description="Hormigas muertas")
    max_ants: int = Field(description="Capacidad máxima de hormigas")
    food_stock: int = Field(description="Stock actual de comida")
    can_create_more: bool = Field(description="Si se pueden crear más hormigas")
    emergency_mode: bool = Field(description="Si la colonia está en modo emergencia")
    ants_by_subsystem: Dict[str, int] = Field(description="Distribución de hormigas por subsistema")
    ant_lifespan_minutes: float = Field(description="Tiempo de vida de hormigas en minutos")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "total_ants": 15,
                "alive_ants": 12,
                "free_ants": 5,
                "assigned_ants": 7,
                "dead_ants": 3,
                "max_ants": 100,
                "food_stock": 850,
                "can_create_more": True,
                "emergency_mode": False,
                "ants_by_subsystem": {
                    "defense": 3,
                    "communication": 2,
                    "collection": 2
                },
                "ant_lifespan_minutes": 1.5
            }
        }


class SubsystemInfo(BaseModel):
    """Información de un subsistema"""
    id: str = Field(description="ID del subsistema")
    name: str = Field(description="Nombre del subsistema")
    priority_level: int = Field(description="Nivel de prioridad (1=máxima)")


class SubsystemsResponse(BaseModel):
    """Respuesta con información de subsistemas disponibles"""
    available_subsystems: List[SubsystemInfo] = Field(description="Lista de subsistemas disponibles")
    priority_explanation: Dict[str, str] = Field(description="Explicación de niveles de prioridad")


class ConfigurationResponse(BaseModel):
    """Respuesta para cambios de configuración"""
    message: str = Field(description="Mensaje de confirmación")
    changes: Dict[str, Any] = Field(description="Cambios aplicados")
    current_status: ComprehensiveColonyStatus = Field(description="Estado actual después de cambios")

class ServiceResponse(BaseModel):
    """Respuesta para cambios de servicio"""
    message: str = Field(description="Mensaje de confirmación")
    changes: Dict[str, Any] = Field(description="Cambios aplicados")


class FoodResponse(BaseModel):
    """Respuesta para operaciones de comida"""
    message: str = Field(description="Mensaje de confirmación")
    total_food_stock: int = Field(description="Stock total de comida después de la operación")


class CleanupResponse(BaseModel):
    """Respuesta para operaciones de limpieza"""
    message: str = Field(description="Mensaje de confirmación")
    remaining_ants: int = Field(description="Hormigas restantes después de limpieza")


class ErrorResponse(BaseModel):
    """Modelo estándar para respuestas de error"""
    detail: str = Field(description="Descripción del error")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "detail": "Unknown subsystem: InvalidSystem. Valid options: communication, collection, defense"
            }
        }


class RootResponse(BaseModel):
    """Respuesta del endpoint raíz"""
    message: str = Field(description="Mensaje de bienvenida")
    version: str = Field(description="Versión del subsistema")
    subsystem: str = Field(description="Nombre del subsistema")
    available_subsystems: List[str] = Field(description="Subsistemas disponibles")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "message": "Queen Ant Subsystem - Ant Colony Management System",
                "version": "2.0.0",
                "subsystem": "Queen Ant (Hormiga Reina)",
                "available_subsystems": ["communication", "collection", "defense"]
            }
        }