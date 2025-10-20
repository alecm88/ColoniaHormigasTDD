from typing import Dict, List, Optional, Any
from src.ant import Ant


class Colony:
    def __init__(self, max_ants: int = 10):
        self.max_ants = max_ants
        self.ants: Dict[str, Ant] = {}

    def create_ant(self) -> Optional[Ant]:
        # First cleanup dead ants
        self.cleanup_dead_ants()

        # Check if we can create more ants
        if len(self.ants) >= self.max_ants:
            return None

        ant = Ant()
        self.ants[ant.id] = ant
        return ant

    def cleanup_dead_ants(self) -> int:
        dead_ant_ids = [ant_id for ant_id, ant in self.ants.items() if not ant.is_alive]
        for ant_id in dead_ant_ids:
            del self.ants[ant_id]
        return len(dead_ant_ids)

    def get_alive_ants(self) -> List[Ant]:
        return [ant for ant in self.ants.values() if ant.is_alive]

    def get_ant_by_id(self, ant_id: str) -> Optional[Ant]:
        ant = self.ants.get(ant_id)
        if ant and ant.is_alive:
            return ant
        return None

    def get_status(self) -> Dict[str, Any]:
        alive_ants = self.get_alive_ants()
        total_ants = len(self.ants)
        alive_count = len(alive_ants)
        dead_count = total_ants - alive_count

        return {
            'total_ants': total_ants,
            'alive_ants': alive_count,
            'dead_ants': dead_count,
            'max_ants': self.max_ants,
            'can_create_more': alive_count < self.max_ants
        }