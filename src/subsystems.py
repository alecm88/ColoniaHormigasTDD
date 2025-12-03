from enum import Enum
from typing import Optional
from dataclasses import dataclass


class SubsystemType(Enum):
    COMMUNICATION = "S01_COM"
    COLLECTION = "S02_REC"
    QUEEN = "S03_REI"
    HABITAT = "S04_ENT" #Environment could be reserved keyword
    DEFENSE = "S05_DEF"


@dataclass
## Definimos un subsistema con su prioridad
class Subsystem:
    id: SubsystemType
    name: str
    priority_level: int  # 1 = highest priority, 3 = lowest

    @classmethod
    def get_known_subsystems(cls):
        return {
            SubsystemType.COMMUNICATION: cls(SubsystemType.COMMUNICATION, "S01_COM", 2),
            SubsystemType.COLLECTION: cls(SubsystemType.COLLECTION, "S02_REC", 3),
            SubsystemType.QUEEN: cls(SubsystemType.QUEEN, "S03_REI", 3),
            SubsystemType.HABITAT: cls(SubsystemType.HABITAT, "S04_ENT", 3),
            SubsystemType.DEFENSE: cls(SubsystemType.DEFENSE, "S05_DEF", 1)  # Highest priority
        }

    @classmethod
    def get_by_name(cls, name: str) -> Optional['Subsystem']:
        known = cls.get_known_subsystems()
        for subsystem in known.values():
            if subsystem.name.lower() == name.lower():
                return subsystem
        return None

    @classmethod
    def get_by_id(cls, subsystem_id: SubsystemType) -> Optional['Subsystem']:
        known = cls.get_known_subsystems()
        return known.get(subsystem_id)
    
    #Definimos como se debe ver el subsistema
    def __str__(self):
        return f"{self.name} (Priority: {self.priority_level})"
    
    #Metodos de comparacion por prioridad
    def __eq__(self, other):
        return self.priority_level == other.priority_level

    def __lt__(self, other):
        return self.priority_level < other.priority_level
    def __gt__(self, other):
        return self.priority_level > other.priority_level
    def __le__(self, other):
        return self.priority_level <= other.priority_level
    def __ge__(self, other):
        return self.priority_level >= other.priority_level