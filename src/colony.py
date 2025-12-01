from typing import Dict, List, Optional, Any
from datetime import datetime
from src.ant import Ant, AntState
from src.subsystems import SubsystemType, Subsystem


class Colony:
    def __init__(self, max_ants: int = 100, initial_food_stock: int = 1000,
                 ant_lifespan_minutes: float = 1.5, food_per_ant: int = 10):
        self.max_ants = max_ants
        self.ant_lifespan_minutes = ant_lifespan_minutes
        self.ants: Dict[str, Ant] = {}
        self.food_stock = initial_food_stock
        self.food_per_ant = food_per_ant  # Food units required to create an ant
        self.emergency_mode = False
        self.subsystems = Subsystem.get_known_subsystems()

    def create_ant(self) -> Optional[Ant]: 
        self.cleanup_dead_ants()

        # Check food availability
        if self.food_stock < self.food_per_ant:
            return None
    
        # Check capacity
        alive_count = len([ant for ant in self.ants.values() if ant.is_alive])
        if alive_count >= self.max_ants:
            return None

        # Create ant and consume food
        ant = Ant(self.ant_lifespan_minutes)
        self.ants[ant.id] = ant
        self.food_stock -= self.food_per_ant
        return ant

    # def create_ant(self, force_creation: bool = False) -> Optional[Ant]:
    #     """Create an ant if resources and capacity allow"""
    #     # First update all ant states and cleanup dead ants
    #     self.update_all_ant_states()
    #     return ant

    def request_ant(self, subsystem_name: str, priority: int = 1,
                   estimated_duration_seconds: float = 60) -> Optional[Ant]:
        """Request an ant for assignment to a subsystem"""
        # Update states first
        # self.update_all_ant_states()

        # Validate subsystem
        subsystem = Subsystem.get_by_name(subsystem_name)
        if not subsystem:
            return None

        # Get available ants that can handle the task
        available_ants = [
            ant for ant in self.ants.values()
            if ant.is_available_for_assignment
        ]

        if not available_ants:
            # Try to create a new ant if we have capacity and food
            new_ant = self.create_ant()
            if new_ant:
                available_ants = [new_ant]

        if not available_ants:
            return None

        # Select best ant (most remaining life)
        best_ant = max(available_ants, key=lambda ant: ant.remaining_life_seconds)

        # Assign ant
        if best_ant.assign_to_subsystem(subsystem.id):
            return best_ant

        return None

    def request_ants(self, subsystem_name: str, quantity: int, priority: int = 1,
                    estimated_duration_seconds: float = 60) -> Dict[str, Any]:
        """Request multiple ants for assignment to a subsystem.

        This method attempts to fulfill the entire request atomically.
        If the full quantity cannot be provided, no ants are assigned.

        Args:
            subsystem_name: Name of the subsystem requesting ants
            quantity: Number of ants requested
            priority: Priority level of the request
            estimated_duration_seconds: Estimated duration of the task

        Returns:
            Dictionary with:
                - success: Boolean indicating if the request was fulfilled
                - ants: List of assigned ants (empty if failed)
                - message: Description of the result
                - ants_used: Number of existing ants used
                - ants_created: Number of new ants created
                - available: Number of available ants before request
                - can_create: Number of ants that can be created
                - requested: Number of ants requested
                - needed: Number of ants needed to fulfill request
        """
        result = {
            'success': False,
            'ants': [],
            'message': '',
            'ants_used': 0,
            'ants_created': 0,
            'available': 0,
            'can_create': 0,
            'requested': quantity,
            'needed': quantity
        }

        # Validate quantity
        if quantity < 0:
            result['message'] = f"Invalid quantity: {quantity}"
            return result

        if quantity == 0:
            result['success'] = True
            result['message'] = "No ants requested"
            return result

        # Update states first
        self.cleanup_dead_ants()

        # Validate subsystem
        subsystem = Subsystem.get_by_name(subsystem_name)
        if not subsystem:
            result['message'] = f"Invalid subsystem: {subsystem_name}"
            return result

        # Get available ants that can handle the task
        available_ants = [
            ant for ant in self.ants.values()
            if ant.is_available_for_assignment
        ]
        result['available'] = len(available_ants)

        # Calculate how many ants we can create
        alive_count = len([ant for ant in self.ants.values() if ant.is_alive])
        capacity_available = self.max_ants - alive_count
        food_available = self.food_stock // self.food_per_ant
        can_create = min(capacity_available, food_available)
        result['can_create'] = can_create

        # Check if we can fulfill the request
        total_available = len(available_ants) + can_create
        if total_available < quantity:
            result['message'] = (f"Cannot fulfill request for {quantity} ants. "
                                f"Available: {len(available_ants)}, Can create: {can_create}")
            return result

        # Prepare lists for transaction
        ants_to_assign = []
        ants_to_create = []

        # Use existing available ants first
        ants_to_use = min(len(available_ants), quantity)
        if ants_to_use > 0:
            # Sort by remaining life to get the best ants
            available_ants.sort(key=lambda ant: ant.remaining_life_seconds, reverse=True)
            ants_to_assign = available_ants[:ants_to_use]
            result['ants_used'] = ants_to_use

        # Calculate how many new ants we need to create
        ants_needed = quantity - ants_to_use
        if ants_needed > 0:
            # Verify we can create them (double-check)
            if ants_needed > can_create:
                result['message'] = f"Internal error: Cannot create {ants_needed} ants"
                return result

            # Create the ants
            for _ in range(ants_needed):
                new_ant = self.create_ant()
                if new_ant:
                    ants_to_create.append(new_ant)
                else:
                    # Rollback: Return created ants to free state
                    # (They're already free by default, but we'll clean up)
                    result['message'] = "Failed to create required ants"
                    return result

            result['ants_created'] = len(ants_to_create)

        # Now assign all ants to the subsystem
        all_ants = ants_to_assign + ants_to_create
        assigned_ants = []

        for ant in all_ants:
            if ant.assign_to_subsystem(subsystem.id):
                assigned_ants.append(ant)
            else:
                # Rollback: Free all previously assigned ants
                for assigned_ant in assigned_ants:
                    assigned_ant.state = AntState.FREE
                    assigned_ant.assigned_to = None
                    assigned_ant.assignment_time = None

                result['message'] = f"Failed to assign ant {ant.id}"
                return result

        # Success!
        result['success'] = True
        result['ants'] = assigned_ants
        result['message'] = f"Successfully assigned {len(assigned_ants)} ants"

        return result

    def return_ant(self, ant_id: str, returned_with_food: int = 0,
                  died_in_mission: bool = False) -> bool:
        """Return an ant from assignment"""
        ant = self.ants.get(ant_id)
        if not ant:
            return False

        # Add food if ant returned with food
        food_gained = ant.return_from_assignment(died_in_mission, returned_with_food)
        if food_gained:
            self.food_stock += food_gained   # Food gained from successful collection

        return True

    def activate_emergency_mode(self) -> None:
        self.emergency_mode = True
        return
    
    def deactivate_emergency_mode(self) -> None:
        self.emergency_mode = False
        return

    def request_emergency_ants(self, requesting_subsystem: str,
                             number_needed: int) -> List[Ant]:
        
        # Validate subsystem
        subsystem = Subsystem.get_by_name(requesting_subsystem)
        if not subsystem:
            return None
        
        """Handle emergency ant requests with reassignment from lower priority tasks"""
        self.emergency_mode = True
        emergency_ants = []

        # First get all available ants
        available_ants = [
            ant for ant in self.ants.values()
            if ant.is_available_for_assignment
        ]
        emergency_ants.extend(available_ants[:number_needed])

        # If we need more ants, reassign from lower priority subsystems
        if len(emergency_ants) < number_needed:
            reassignable_ants = self._get_reassignable_ants(requesting_subsystem)
            needed = number_needed - len(emergency_ants)
            emergency_ants.extend(reassignable_ants[:needed])

        # Assign all emergency ants to the requesting subsystem
        requesting_subsystem_enum = None
        for subsystem_type, subsystem in self.subsystems.items():
            if subsystem.name.lower() == requesting_subsystem.lower():
                requesting_subsystem_enum = subsystem_type
                break

        if requesting_subsystem_enum:
            for ant in emergency_ants:
                ant.assign_to_subsystem(requesting_subsystem_enum, True)

        return emergency_ants

    def _get_reassignable_ants(self, requesting_subsystem: str) -> List[Ant]:
        """Get ants that can be reassigned based on priority"""
        requesting_priority = 3  # Default to lowest priority
        for subsystem in self.subsystems.values():
            if subsystem.name.lower() == requesting_subsystem.lower():
                requesting_priority = subsystem.priority_level
                break

        reassignable = []
        for ant in self.ants.values():
            if (ant.state == AntState.ASSIGNED and ant.assigned_to and
                ant.assignment_time):
                # Check if assigned subsystem has lower priority
                assigned_subsystem = self.subsystems.get(ant.assigned_to)
                if (assigned_subsystem and
                    assigned_subsystem.priority_level > requesting_priority):

                    reassignable.append(ant)

        return reassignable


    def cleanup_dead_ants(self) -> int:
        """Remove dead ants from the colony"""
        dead_ant_ids = [ant_id for ant_id, ant in self.ants.items() if not ant.is_alive]
        for ant_id in dead_ant_ids:
            del self.ants[ant_id]
        return len(dead_ant_ids)

    def get_alive_ants(self) -> List[Ant]:
        """Get all living ants"""
        return [ant for ant in self.ants.values() if ant.is_alive]

    def get_free_ants(self) -> List[Ant]:
        """Get all free (unassigned) living ants"""
        return [ant for ant in self.ants.values() if ant.is_available_for_assignment]

    def get_assigned_ants(self) -> List[Ant]:
        """Get all assigned ants"""
        return [ant for ant in self.ants.values() if ant.state == AntState.ASSIGNED and ant.is_alive]

    def get_ant_by_id(self, ant_id: str) -> Optional[Ant]:
        """Get ant by ID if it exists and is alive"""
        ant = self.ants.get(ant_id)
        if ant and ant.is_alive:
            return ant
        return None

    def add_food(self, amount: int):
        """Add food to the colony stock"""
        self.food_stock += amount

    def activate_emergency_mode(self):
        """Activate emergency mode for the colony"""
        self.emergency_mode = True

    def deactivate_emergency_mode(self):
        """Deactivate emergency mode for the colony"""
        self.emergency_mode = False

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get detailed colony status"""
        # self.update_all_ant_states()

        alive_ants = self.get_alive_ants()
        free_ants = self.get_free_ants()
        assigned_ants = self.get_assigned_ants()

        # Count ants by subsystem
        ants_by_subsystem = {}
        for subsystem_type in SubsystemType:
            count = len([ant for ant in assigned_ants if ant.assigned_to == subsystem_type])
            ants_by_subsystem[subsystem_type.value] = count

        return {
            'total_ants': len(self.ants),
            'alive_ants': len(alive_ants),
            'free_ants': len(free_ants),
            'assigned_ants': len(assigned_ants),
            'dead_ants': len(self.ants) - len(alive_ants),
            'max_ants': self.max_ants,
            'food_stock': self.food_stock,
            'can_create_more': len(alive_ants) < self.max_ants and self.food_stock >= self.food_per_ant,
            'emergency_mode': self.emergency_mode,
            'ants_by_subsystem': ants_by_subsystem,
            'ant_lifespan_minutes': self.ant_lifespan_minutes
        }

    def get_status(self) -> Dict[str, Any]:
        alive_ants = self.get_alive_ants()
        free_ants = self.get_free_ants()
        assigned_ants = self.get_assigned_ants()

        return {
            'total_ants': len(self.ants),
            'alive_ants': len(alive_ants),
            'free_ants': len(free_ants),
            'assigned_ants': len(assigned_ants),
            'dead_ants': len(self.ants) - len(alive_ants),
            'max_ants': self.max_ants,
            'food_stock': self.food_stock,
        }