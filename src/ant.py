import uuid
from datetime import datetime
from typing import Dict, Any


class Ant:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.birth_time = datetime.now()
        self.lifespan = 90  # 1 minute 30 seconds

    @property
    def is_alive(self) -> bool:
        age = (datetime.now() - self.birth_time).total_seconds()
        return age < self.lifespan

    @property
    def age_seconds(self) -> float:
        return (datetime.now() - self.birth_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'birth_time': self.birth_time.isoformat(),
            'is_alive': self.is_alive,
            'age_seconds': self.age_seconds
        }