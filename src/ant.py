import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum
from src.subsystems import SubsystemType


class AntState(Enum):
    FREE = "free"
    ASSIGNED = "assigned"
    DEAD = "dead"


class Ant:
    def __init__(self, lifespan_minutes: float = 1.5):
        self.id = str(uuid.uuid4())
        self.birth_time = datetime.now()
        self.lifespan_seconds = lifespan_minutes * 60  # Convert minutes to seconds
        self.state = AntState.FREE
        self.assigned_to: Optional[SubsystemType] = None
        self.assignment_time: Optional[datetime] = None
        # self.wait_time_seconds = 10  # 10 seconds wait time as specified

    @property
    def is_alive(self) -> bool:
        if self.state == AntState.DEAD:
            return False
        age = (datetime.now() - self.birth_time).total_seconds()
        return age < self.lifespan_seconds

    @property
    def age_seconds(self) -> float:
        return (datetime.now() - self.birth_time).total_seconds()

    @property
    def remaining_life_seconds(self) -> float:
        remaining = self.lifespan_seconds - self.age_seconds
        return max(0, remaining)

    @property
    def death_time(self) -> datetime:
        return self.birth_time + timedelta(seconds=self.lifespan_seconds)

    @property
    def is_available_for_assignment(self) -> bool:
        return self.is_alive and self.state == AntState.FREE

    def assign_to_subsystem(self, subsystem: SubsystemType, emergency: bool = False) -> bool:
        """Assign ant to a subsystem if available"""
        if not self.is_available_for_assignment and not emergency:
            return False

        self.state = AntState.ASSIGNED
        self.assigned_to = subsystem
        self.assignment_time = datetime.now()
        return True

    def return_from_assignment(self, died_in_mission: bool = False, returned_with_food: int = 0):
        """Return ant from assignment, potentially with food or as dead"""
        if died_in_mission:
            self.state = AntState.DEAD
        else:
            self.state = AntState.FREE

        self.assigned_to = None
        self.assignment_time = None
        return returned_with_food


    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'birth_time': self.birth_time.isoformat(),
            'death_time': self.death_time.isoformat(),
            'is_alive': self.is_alive,
            'age_seconds': self.age_seconds,
            'remaining_life_seconds': self.remaining_life_seconds,
            'state': self.state.value,
            'assigned_to': self.assigned_to.value if self.assigned_to and self.assigned_to.value else None,
            'assignment_time': self.assignment_time.isoformat() if self.assignment_time else None,
            # 'wait_time_seconds': self.wait_time_seconds
        }