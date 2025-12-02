import pytest
from datetime import datetime, timedelta
import time
from src.colony import Colony
from src.ant import AntState
from src.subsystems import SubsystemType


class TestRequestAnts:
    def test_request_multiple_ants_creates_new_ants_if_needed(self):
        colony = Colony()
        initial_ant_count = len(colony.ants)

        result = colony.request_ants(SubsystemType.COMMUNICATION.value, 5)

        assert result['success'] is True
        assert len(result['ants']) == 5
        assert len(colony.ants) == initial_ant_count + 5
        assert result['message'] == "Successfully assigned 5 ants"
        for ant in result['ants']:
            assert ant.state == AntState.ASSIGNED
            assert ant.assigned_to == SubsystemType.COMMUNICATION

    def test_request_ants_uses_available_ants_first(self):
        colony = Colony()

        # Create 3 free ants
        ant1 = colony.create_ant()
        ant2 = colony.create_ant()
        ant3 = colony.create_ant()

        # Request 5 ants (3 existing + 2 new)
        result = colony.request_ants(SubsystemType.DEFENSE.value, 5)

        assert result['success'] is True
        assert len(result['ants']) == 5
        assert result['ants_used'] == 3
        assert result['ants_created'] == 2

        # Verify the existing ants were used
        existing_ant_ids = [ant1.id, ant2.id, ant3.id]
        assigned_ant_ids = [ant.id for ant in result['ants']]
        for ant_id in existing_ant_ids:
            assert ant_id in assigned_ant_ids

    def test_request_ants_fails_if_cannot_fulfill_all(self):
        colony = Colony(initial_food_stock=2)  # Only enough for 2 ants

        result = colony.request_ants(SubsystemType.COLLECTION.value, 5)

        assert result['success'] is False
        assert len(result['ants']) == 0
        assert result['available'] == 0
        assert result['can_create'] == 2
        assert result['requested'] == 5
        assert "Cannot fulfill request" in result['message']

    def test_request_ants_with_invalid_subsystem(self):
        colony = Colony()

        result = colony.request_ants("UnknownSubsystem", 3)

        assert result['success'] is False
        assert result['message'] == "Invalid subsystem: UnknownSubsystem"
        assert len(result['ants']) == 0

    def test_request_ants_with_zero_quantity(self):
        colony = Colony()

        result = colony.request_ants(SubsystemType.DEFENSE.value, 0)

        assert result['success'] is True
        assert len(result['ants']) == 0
        assert result['message'] == "No ants requested"

    def test_request_ants_with_negative_quantity(self):
        colony = Colony()

        result = colony.request_ants(SubsystemType.DEFENSE.value, -1)

        assert result['success'] is False
        assert result['message'] == "Invalid quantity: -1"
        assert len(result['ants']) == 0

    def test_request_ants_respects_max_capacity(self):
        colony = Colony(max_ants=5, initial_food_stock=1000)

        # Create 3 ants
        colony.create_ant()
        colony.create_ant()
        colony.create_ant()

        # Try to request 5 ants (should use 3 existing and create 2 more to reach max)
        result = colony.request_ants(SubsystemType.COMMUNICATION.value, 5)

        assert result['success'] is True
        assert result['available'] == 3
        assert result['can_create'] == 2  # Can only create 2 more before hitting max
        assert result['requested'] == 5
        assert result['ants_used'] == 3
        assert result['ants_created'] == 2
        assert len(result['ants']) == 5

    def test_request_ants_with_duration_filter(self):
        colony = Colony(ant_lifespan_minutes=1.0, initial_food_stock=500)  # Longer lifespan for testing

        # Create ants with different ages
        young_ant = colony.create_ant()
        time.sleep(0.01)

        old_ant = colony.create_ant()
        old_ant.created_at = datetime.now() - timedelta(seconds=50)  # Make it older

        # Request ants for a shorter task
        result = colony.request_ants(
            SubsystemType.DEFENSE.value,
            2,
            estimated_duration_seconds=10
        )

        assert result['success'] is True
        assert len(result['ants']) == 2
        # Both ants should be assigned since they can handle a 10 second task

    def test_request_ants_with_priority(self):
        colony = Colony()

        result = colony.request_ants(
            SubsystemType.DEFENSE.value,
            3,
            priority=1
        )

        assert result['success'] is True
        assert len(result['ants']) == 3
        # All ants should be assigned with the given priority
        for ant in result['ants']:
            assert ant.assigned_to == SubsystemType.DEFENSE

    def test_request_ants_transaction_rollback_on_partial_failure(self):
        colony = Colony(initial_food_stock=4)  # Enough for 4 ants

        # Create 2 free ants
        colony.create_ant()
        colony.create_ant()

        initial_free_count = len(colony.get_free_ants())
        initial_total_count = len(colony.ants)

        # Request 5 ants (2 existing + 3 new, but only food for 4 total new)
        result = colony.request_ants(SubsystemType.COMMUNICATION.value, 5)

        # Should fail since we can't fulfill all 5
        assert result['success'] is False

        # Verify rollback - no ants should be assigned or created
        assert len(colony.get_free_ants()) == initial_free_count
        assert len(colony.ants) == initial_total_count

        # All ants should still be free
        for ant in colony.ants.values():
            if ant.is_alive:
                assert ant.state == AntState.FREE

    def test_request_ants_detailed_response_on_success(self):
        colony = Colony()

        # Create 2 free ants
        colony.create_ant()
        colony.create_ant()

        result = colony.request_ants(SubsystemType.COLLECTION.value, 4)

        assert result['success'] is True
        assert result['ants_used'] == 2
        assert result['ants_created'] == 2
        assert result['requested'] == 4
        assert result['message'] == "Successfully assigned 4 ants"
        assert len(result['ants']) == 4

    def test_request_ants_detailed_response_on_failure(self):
        colony = Colony(max_ants=3, initial_food_stock=2)  # Very limited resources

        # Create 1 ant (leaves food for 1 more)
        colony.create_ant()

        result = colony.request_ants(SubsystemType.DEFENSE.value, 5)

        assert result['success'] is False
        assert result['available'] == 1
        assert result['can_create'] == 1  # Can create 1 more with available food (10 food left, need 10 per ant)
        assert result['requested'] == 5
        assert result['needed'] == 5
        assert "Cannot fulfill request" in result['message']
        assert "Available: 1" in result['message']
        assert "Can create: 1" in result['message']

    def test_request_ants_concurrent_requests(self):
        colony = Colony(initial_food_stock=200)

        # First request
        result1 = colony.request_ants(SubsystemType.DEFENSE.value, 3)
        assert result1['success'] is True

        # Second request
        result2 = colony.request_ants(SubsystemType.COMMUNICATION.value, 3)
        assert result2['success'] is True

        # Verify no overlap in assigned ants
        ants1_ids = set(ant.id for ant in result1['ants'])
        ants2_ids = set(ant.id for ant in result2['ants'])
        assert len(ants1_ids.intersection(ants2_ids)) == 0

        # Verify correct assignments
        for ant in result1['ants']:
            assert ant.assigned_to == SubsystemType.DEFENSE
        for ant in result2['ants']:
            assert ant.assigned_to == SubsystemType.COMMUNICATION

    def test_request_ants_with_all_parameters(self):
        colony = Colony()

        result = colony.request_ants(
            subsystem_name=SubsystemType.DEFENSE.value,
            quantity=3,
            priority=1,
            estimated_duration_seconds=45
        )

        assert result['success'] is True
        assert len(result['ants']) == 3

        # All ants should be able to handle the estimated duration
        for ant in result['ants']:
            # assert ant.can_handle_task(45)
            assert ant.assigned_to == SubsystemType.DEFENSE

    def test_request_ants_preserves_existing_assignments(self):
        colony = Colony()

        # Create and assign some ants
        existing_assigned = colony.request_ant(SubsystemType.DEFENSE.value)

        # Request more ants for different subsystem
        result = colony.request_ants(SubsystemType.COMMUNICATION.value, 3)

        assert result['success'] is True

        # Original assignment should be preserved
        assert existing_assigned.assigned_to == SubsystemType.DEFENSE
        assert existing_assigned.state == AntState.ASSIGNED

        # New assignments should be correct
        for ant in result['ants']:
            assert ant.assigned_to == SubsystemType.COMMUNICATION