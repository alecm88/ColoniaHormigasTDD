import pytest
from datetime import datetime, timedelta
from src.colony import Colony
from src.ant import AntState
from src.subsystems import SubsystemType


class TestColonyExtended:
    def test_colony_creation_with_requirements(self):
        colony = Colony(max_ants=100, initial_food_stock=1000, ant_lifespan_minutes=1.5, food_per_ant=5)

        assert colony.max_ants == 100
        assert colony.food_stock == 1000
        assert colony.ant_lifespan_minutes == 1.5
        assert colony.food_per_ant == 5
        assert colony.emergency_mode is False

    def test_request_ant_for_known_subsystem(self):
        colony = Colony()
        ant1 = colony.create_ant()

        ant = colony.request_ant("S05_DEF", priority=1, estimated_duration_seconds=30)

        assert ant is not None
        assert ant.state == AntState.ASSIGNED
        assert ant.assigned_to == SubsystemType.DEFENSE

    def test_request_ant_for_unknown_subsystem_returns_none(self):
        colony = Colony()

        ant = colony.request_ant("UnknownSystem", priority=1)

        assert ant is None

    def test_request_ant_creates_new_ant_if_needed(self):
        colony = Colony()
        initial_ant_count = len(colony.ants)

        ant = colony.request_ant(SubsystemType.COMMUNICATION.value)

        assert ant is not None
        assert len(colony.ants) == initial_ant_count + 1

    def test_request_ant_without_resources(self):
        colony = Colony(initial_food_stock=5)
        initial_ant_count = len(colony.ants)

        ant = colony.request_ant(SubsystemType.COMMUNICATION.value)

        assert ant is None
        assert len(colony.ants) == initial_ant_count

    def test_return_ant_successful_with_food(self):
        colony = Colony()
        ant = colony.request_ant(SubsystemType.COLLECTION.value)
        initial_food = colony.food_stock

        success = colony.return_ant(ant.id, returned_with_food=20)

        assert success is True
        assert ant.state == AntState.FREE
        assert colony.food_stock == initial_food + 20  # Food gained

    def test_return_ant_died_in_mission(self):
        colony = Colony()
        ant = colony.request_ant(SubsystemType.DEFENSE.value)

        success = colony.return_ant(ant.id, died_in_mission=True)

        assert success is True
        assert ant.state == AntState.DEAD

    def test_return_ant_nonexistent_ant_fails(self):
        colony = Colony()
        success = colony.return_ant("nonexistent-id")
        assert success is False

    def test_request_emergency_ants_gets_available_ants_first(self):
        colony = Colony()
        # Create some free ants
        colony.create_ant()
        colony.create_ant()

        emergency_ants = colony.request_emergency_ants("S05_DEF", number_needed=2)

        assert len(emergency_ants) == 2
        assert all(ant.assigned_to == SubsystemType.DEFENSE for ant in emergency_ants)
        assert colony.emergency_mode is True

    def test_request_emergency_ants_reassigns_from_lower_priority(self):
        colony = Colony()
        colony.max_ants = 1

        # Assign ant to Collection (lowest priority)
        collection_ant = colony.request_ant("S02_REC")
        # Make the assignment older
        collection_ant.assignment_time = datetime.now() - timedelta(seconds=15)

        # Request emergency ant for Defense (highest priority)
        emergency_ants = colony.request_emergency_ants("S05_DEF", number_needed=1)

        assert len(emergency_ants) == 1
        assert emergency_ants[0].id == collection_ant.id
        assert emergency_ants[0].assigned_to == SubsystemType.DEFENSE

    def test_emergency_ants_respects_priority_hierarchy(self):
        colony = Colony()

        # Assign ants to different subsystems
        defense_ant = colony.request_ant("S05_DEF")  # Priority 1
        collection_ant = colony.request_ant("S02_REC")  # Priority 3

        # Make assignments old enough
        for ant in [defense_ant, collection_ant]:
            ant.assignment_time = datetime.now() - timedelta(seconds=15)

        # Communication requests emergency ant - should only take from Collection
        emergency_ants = colony.request_emergency_ants("S05_DEF", number_needed=1)

        # Should get the Collection ant, not Defense ant
        assert len(emergency_ants) == 1
        assert emergency_ants[0].id == collection_ant.id

    def test_get_free_ants(self):
        colony = Colony()
        colony.create_ant()
        assigned_ant = colony.request_ant(SubsystemType.DEFENSE.value)
        free_ant1 = colony.create_ant()

        free_ants = colony.get_free_ants()

        assert len(free_ants) == 1
        free_ant_ids = [ant.id for ant in free_ants]
        assert free_ant1.id in free_ant_ids
        assert assigned_ant.id not in free_ant_ids

    def test_get_assigned_ants(self):
        colony = Colony()
        assigned_ant1 = colony.request_ant(SubsystemType.DEFENSE.value)
        assigned_ant2 = colony.request_ant(SubsystemType.COLLECTION.value)
        free_ant = colony.create_ant()

        assigned_ants = colony.get_assigned_ants()

        assert len(assigned_ants) == 2
        assigned_ant_ids = [ant.id for ant in assigned_ants]
        assert assigned_ant1.id in assigned_ant_ids
        assert assigned_ant2.id in assigned_ant_ids
        assert free_ant.id not in assigned_ant_ids


    def test_comprehensive_status_includes_all_information(self):
        colony = Colony()
        colony.request_ant(SubsystemType.DEFENSE.value)  # Assigned ant
        colony.request_ant(SubsystemType.COLLECTION.value)  # Another assigned ant
        colony.create_ant()  # Free ant

        status = colony.get_comprehensive_status()

        expected_keys = {
            'total_ants', 'alive_ants', 'free_ants', 'assigned_ants', 'dead_ants',
            'max_ants', 'food_stock', 'can_create_more', 'emergency_mode',
            'ants_by_subsystem', 'ant_lifespan_minutes'
        }
        assert set(status.keys()) == expected_keys

        assert status['total_ants'] == 3
        assert status['alive_ants'] == 3
        assert status['free_ants'] == 1
        assert status['assigned_ants'] == 2
        assert status['dead_ants'] == 0
        assert status['ants_by_subsystem'][SubsystemType.DEFENSE.value] == 1
        assert status['ants_by_subsystem'][SubsystemType.COLLECTION.value] == 1
        assert status['ants_by_subsystem'][SubsystemType.COMMUNICATION.value] == 0

    def test_can_create_more_considers_food_and_capacity(self):
        # Test with sufficient food and capacity
        colony1 = Colony(max_ants=10, initial_food_stock=100)
        status1 = colony1.get_comprehensive_status()
        assert status1['can_create_more'] is True

        # Test with insufficient food
        colony2 = Colony(max_ants=10, initial_food_stock=5)  # Less than food_per_ant
        status2 = colony2.get_comprehensive_status()
        assert status2['can_create_more'] is False

        # Test with insufficient capacity
        colony3 = Colony(max_ants=1, initial_food_stock=100)
        colony3.create_ant()  # Fill capacity
        status3 = colony3.get_comprehensive_status()
        assert status3['can_create_more'] is False


class TestColonyEmergencyScenarios:
    def test_emergency_mode_activation(self):
        colony = Colony()
        assert colony.emergency_mode is False

        colony.activate_emergency_mode()

        assert colony.emergency_mode is True

    def test_emergency_mode_deactivation(self):
        colony = Colony()
        colony.activate_emergency_mode()
        assert colony.emergency_mode is True

        colony.deactivate_emergency_mode()

        assert colony.emergency_mode is False

    def test_emergency_request_with_no_ants_available(self):
        colony = Colony(initial_food_stock=5)  # Insufficient food to create ants

        emergency_ants = colony.request_emergency_ants("S05_DEF", number_needed=3)

        assert len(emergency_ants) == 0
        assert colony.emergency_mode is True

    def test_emergency_cascade_scenario(self):
        """Test cascading emergency requests from multiple subsystems"""
        colony = Colony()

        # Create and assign ants to all subsystems
        for _ in range(2):
            colony.request_ant("S02_REC")  # Lowest priority
        for _ in range(2):
            colony.request_ant("S01_COM")  # Medium priority

        # Make assignments old enough
        for ant in colony.ants.values():
            if ant.state == AntState.ASSIGNED:
                ant.assignment_time = datetime.now() - timedelta(seconds=20)

        # Defense requests emergency ants (should get from Collection and Communication)
        defense_emergency = colony.request_emergency_ants("S05_DEF", number_needed=3)

        assert len(defense_emergency) >= 2  # Should get at least the Collection ants
        assert colony.emergency_mode is True

        # Verify Collection ants were reassigned first
        collection_count = sum(1 for ant in colony.ants.values()
                               if ant.assigned_to == SubsystemType.COLLECTION)
        assert collection_count == 0  # All Collection ants should be reassigned

    def test_emergency_request_invalid_subsystem(self):
        colony = Colony()
        colony.create_ant()

        emergency_ants = colony.request_emergency_ants("InvalidSubsystem", number_needed=1)

        assert emergency_ants is None
        assert colony.emergency_mode is False  # Should not activate for invalid request

    def test_emergency_partial_fulfillment(self):
        """Test when only partial number of requested ants can be provided"""
        colony = Colony()

        # Create only 2 ants
        colony.create_ant()
        colony.create_ant()

        # Request 5 emergency ants
        emergency_ants = colony.request_emergency_ants("S05_DEF", number_needed=5)

        assert len(emergency_ants) == 2  # Only 2 available
        assert all(ant.assigned_to == SubsystemType.DEFENSE for ant in emergency_ants)
        assert colony.emergency_mode is True

    def test_emergency_with_dead_ants(self):
        colony = Colony(ant_lifespan_minutes=0.01)  # Very short lifespan

        # Create ants and let them die
        ant1 = colony.create_ant()
        ant2 = colony.create_ant()

        import time
        time.sleep(1)  # Wait for ants to die

        colony.cleanup_dead_ants()

        # Try to request emergency ants
        emergency_ants = colony.request_emergency_ants("S05_DEF", number_needed=2)

        assert len(emergency_ants) == 0  # No living ants available
        assert colony.emergency_mode is True

    def test_emergency_priority_preservation(self):
        """Test that higher priority subsystems don't get reassigned"""
        colony = Colony()

        # Assign ant to Defense (highest priority)
        defense_ant = colony.request_ant("S05_DEF")
        defense_ant.assignment_time = datetime.now() - timedelta(seconds=30)

        # Collection tries to request emergency ant
        emergency_ants = colony.request_emergency_ants("S02_REC", number_needed=1)

        assert len(emergency_ants) == 0  # Cannot take from higher priority
        assert defense_ant.assigned_to == SubsystemType.DEFENSE  # Still assigned to Defense

    def test_emergency_mode_affects_new_ant_creation(self):
        colony = Colony(max_ants=5, initial_food_stock=100)

        # Fill colony to near capacity
        for _ in range(4):
            colony.create_ant()

        colony.activate_emergency_mode()

        # In emergency mode, might have different creation rules
        new_ant = colony.create_ant()
        assert new_ant is not None
        assert len(colony.ants) == 5

    def test_simultaneous_emergency_requests(self):
        """Test handling multiple emergency requests at once"""
        colony = Colony()

        # Create a pool of ants
        for _ in range(6):
            colony.create_ant()

        # Multiple emergency requests
        defense_ants = colony.request_emergency_ants("S05_DEF", number_needed=2)
        comm_ants = colony.request_emergency_ants("S01_COM", number_needed=2)

        assert len(defense_ants) == 2
        assert len(comm_ants) == 2
        assert colony.emergency_mode is True

        # Verify no ant is assigned to multiple subsystems
        all_emergency_ants = defense_ants + comm_ants
        ant_ids = [ant.id for ant in all_emergency_ants]
        assert len(ant_ids) == len(set(ant_ids))  # All IDs are unique

    def test_emergency_reassignment_tracking(self):
        """Test that emergency reassignments are properly tracked"""
        colony = Colony()

        # Create and assign ant
        ant = colony.request_ant("S02_REC")
        original_assignment = ant.assigned_to
        ant.assignment_time = datetime.now() - timedelta(seconds=20)

        # Track reassignment
        emergency_ants = colony.request_emergency_ants("S05_DEF", number_needed=1)

        assert len(emergency_ants) == 1
        reassigned_ant = emergency_ants[0]
        assert reassigned_ant.id == ant.id
        assert reassigned_ant.assigned_to == SubsystemType.DEFENSE
        assert reassigned_ant.assigned_to != original_assignment

    def test_emergency_food_conservation(self):
        """Test that emergency mode might affect food consumption"""
        colony = Colony(initial_food_stock=25)  # Limited food

        colony.activate_emergency_mode()

        # Create ants during emergency
        ant1 = colony.create_ant()
        ant2 = colony.create_ant()

        assert ant1 is not None
        assert ant2 is not None
        assert colony.food_stock == 5  # 30 - 20 (2 ants * 10 food each)

        # Try to create third ant with insufficient food
        ant3 = colony.create_ant()
        assert ant3 is None
        assert colony.food_stock == 5  # Unchanged

    def test_emergency_clear_after_resolution(self):
        """Test clearing emergency mode after crisis resolution"""
        colony = Colony()

        # Create emergency situation
        colony.activate_emergency_mode()
        assert colony.emergency_mode is True

        # Add resources and clear emergency
        colony.add_food(500)
        for _ in range(5):
            colony.create_ant()

        colony.deactivate_emergency_mode()

        assert colony.emergency_mode is False
        assert colony.food_stock > 0
        assert len(colony.get_free_ants()) > 0