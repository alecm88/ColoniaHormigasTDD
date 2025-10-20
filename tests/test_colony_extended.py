import pytest
from datetime import datetime, timedelta
from src.colony import Colony
from src.ant import AntState
from src.subsystems import SubsystemType


class TestColonyExtended:
    def test_colony_creation_with_academic_requirements(self):
        colony = Colony(max_ants=100, initial_food_stock=1000, ant_lifespan_minutes=1.5)

        assert colony.max_ants == 100
        assert colony.food_stock == 1000
        assert colony.ant_lifespan_minutes == 1.5
        assert colony.food_per_ant == 10
        assert colony.emergency_mode is False
        assert len(colony.subsystems) == 3

    def test_create_ant_consumes_food(self):
        colony = Colony(initial_food_stock=100)
        initial_food = colony.food_stock

        ant = colony.create_ant()

        assert ant is not None
        assert colony.food_stock == initial_food - colony.food_per_ant

    def test_cannot_create_ant_without_sufficient_food(self):
        colony = Colony(initial_food_stock=5)  # Less than food_per_ant (10)

        ant = colony.create_ant()

        assert ant is None
        assert colony.food_stock == 5  # Unchanged

    def test_request_ant_for_known_subsystem(self):
        colony = Colony()

        ant = colony.request_ant("Defense", priority=1, estimated_duration_seconds=30)

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

        ant = colony.request_ant("Communication")

        assert ant is not None
        assert len(colony.ants) == initial_ant_count + 1

    def test_request_ant_uses_existing_ant_with_most_remaining_life(self):
        colony = Colony()

        # Create two ants with different ages
        ant1 = colony.create_ant()
        import time
        time.sleep(0.1)  # Make ant1 slightly older
        ant2 = colony.create_ant()

        # Request ant - should get the newer one (ant2) with more remaining life
        assigned_ant = colony.request_ant("Defense")

        assert assigned_ant.id == ant2.id

    def test_request_ant_fails_when_insufficient_remaining_life(self):
        colony = Colony(ant_lifespan_minutes=0.02)  # Very short lifespan
        ant = colony.create_ant()

        # Wait for ant to have very little life left
        import time
        time.sleep(1)

        # Request ant for long task - should fail
        assigned_ant = colony.request_ant("Defense", estimated_duration_seconds=30)

        assert assigned_ant is None

    def test_return_ant_successful_with_food(self):
        colony = Colony()
        ant = colony.request_ant("Collection")
        initial_food = colony.food_stock

        success = colony.return_ant(ant.id, returned_with_food=True)

        assert success is True
        assert ant.state == AntState.FREE
        assert colony.food_stock == initial_food + 20  # Food gained

    def test_return_ant_died_in_mission(self):
        colony = Colony()
        ant = colony.request_ant("Defense")

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

        emergency_ants = colony.request_emergency_ants("Defense", number_needed=2)

        assert len(emergency_ants) == 2
        assert all(ant.assigned_to == SubsystemType.DEFENSE for ant in emergency_ants)
        assert colony.emergency_mode is True

    def test_request_emergency_ants_reassigns_from_lower_priority(self):
        colony = Colony()

        # Assign ant to Collection (lowest priority)
        collection_ant = colony.request_ant("Collection")
        # Make the assignment old enough to be reassignable
        collection_ant.assignment_time = datetime.now() - timedelta(seconds=15)

        # Request emergency ant for Defense (highest priority)
        emergency_ants = colony.request_emergency_ants("Defense", number_needed=1)

        assert len(emergency_ants) == 1
        assert emergency_ants[0].id == collection_ant.id
        assert emergency_ants[0].assigned_to == SubsystemType.DEFENSE

    def test_emergency_ants_respects_priority_hierarchy(self):
        colony = Colony()

        # Assign ants to different subsystems
        defense_ant = colony.request_ant("Defense")  # Priority 1
        comm_ant = colony.request_ant("Communication")  # Priority 2
        collection_ant = colony.request_ant("Collection")  # Priority 3

        # Make assignments old enough
        for ant in [defense_ant, comm_ant, collection_ant]:
            ant.assignment_time = datetime.now() - timedelta(seconds=15)

        # Communication requests emergency ant - should only take from Collection
        emergency_ants = colony.request_emergency_ants("Communication", number_needed=1)

        # Should get the Collection ant, not Defense ant
        assert len(emergency_ants) == 1
        assert emergency_ants[0].id == collection_ant.id

    def test_get_free_ants(self):
        colony = Colony()
        free_ant1 = colony.create_ant()
        assigned_ant = colony.request_ant("Defense")
        free_ant2 = colony.create_ant()

        free_ants = colony.get_free_ants()

        assert len(free_ants) == 2
        free_ant_ids = [ant.id for ant in free_ants]
        assert free_ant1.id in free_ant_ids
        assert free_ant2.id in free_ant_ids
        assert assigned_ant.id not in free_ant_ids

    def test_get_assigned_ants(self):
        colony = Colony()
        free_ant = colony.create_ant()
        assigned_ant1 = colony.request_ant("Defense")
        assigned_ant2 = colony.request_ant("Communication")

        assigned_ants = colony.get_assigned_ants()

        assert len(assigned_ants) == 2
        assigned_ant_ids = [ant.id for ant in assigned_ants]
        assert assigned_ant1.id in assigned_ant_ids
        assert assigned_ant2.id in assigned_ant_ids
        assert free_ant.id not in assigned_ant_ids

    def test_add_food(self):
        colony = Colony(initial_food_stock=100)

        colony.add_food(50)

        assert colony.food_stock == 150

    def test_comprehensive_status_includes_all_information(self):
        colony = Colony()
        colony.create_ant()  # Free ant
        colony.request_ant("Defense")  # Assigned ant
        colony.request_ant("Communication")  # Another assigned ant

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
        assert status['ants_by_subsystem']['defense'] == 1
        assert status['ants_by_subsystem']['communication'] == 1
        assert status['ants_by_subsystem']['collection'] == 0

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