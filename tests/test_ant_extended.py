import pytest
from datetime import datetime, timedelta
from src.ant import Ant, AntState
from src.subsystems import SubsystemType


class TestAntExtended:
    def test_ant_creation_with_custom_lifespan(self):
        ant = Ant(lifespan_minutes=2.0)  # 2 minutes
        assert ant.lifespan_seconds == 120  # 2 * 60
        assert ant.state == AntState.FREE
        assert ant.assigned_to is None

    def test_ant_remaining_life_calculation(self):
        ant = Ant(lifespan_minutes=1.0)  # 60 seconds
        # Should have almost full life initially
        assert ant.remaining_life_seconds > 59
        assert ant.remaining_life_seconds <= 60

    def test_ant_death_time_calculation(self):
        ant = Ant(lifespan_minutes=1.5)  # 90 seconds
        expected_death = ant.birth_time + timedelta(seconds=90)
        assert ant.death_time == expected_death

    def test_ant_is_available_for_assignment_when_free_and_alive(self):
        ant = Ant()
        assert ant.is_available_for_assignment is True

    def test_ant_is_not_available_when_assigned(self):
        ant = Ant()
        ant.assign_to_subsystem(SubsystemType.DEFENSE)
        assert ant.is_available_for_assignment is False

    def test_ant_is_not_available_when_dead(self):
        ant = Ant()
        ant.state = AntState.DEAD
        assert ant.is_available_for_assignment is False

    def test_assign_ant_to_subsystem_success(self):
        ant = Ant()
        success = ant.assign_to_subsystem(SubsystemType.COMMUNICATION)

        assert success is True
        assert ant.state == AntState.ASSIGNED
        assert ant.assigned_to == SubsystemType.COMMUNICATION
        assert ant.assignment_time is not None

    def test_assign_ant_to_subsystem_fails_when_not_available(self):
        ant = Ant()
        ant.state = AntState.ASSIGNED  # Already assigned
        success = ant.assign_to_subsystem(SubsystemType.DEFENSE)

        assert success is False
        assert ant.assigned_to != SubsystemType.DEFENSE

    def test_return_ant_from_assignment_successful(self):
        ant = Ant()
        ant.assign_to_subsystem(SubsystemType.COLLECTION)

        food_gained = ant.return_from_assignment(returned_with_food=10)

        assert ant.state == AntState.FREE
        assert ant.assigned_to is None
        assert ant.assignment_time is None
        assert food_gained == 10

    def test_return_ant_from_assignment_died_in_mission(self):
        ant = Ant()
        ant.assign_to_subsystem(SubsystemType.DEFENSE)

        food_gained = ant.return_from_assignment(died_in_mission=True)

        assert ant.state == AntState.DEAD
        assert ant.assigned_to is None
        assert ant.assignment_time is None
        assert food_gained == 0

    def test_ant_to_dict_includes_all_new_fields(self):
        ant = Ant(lifespan_minutes=2.0)
        ant.assign_to_subsystem(SubsystemType.COMMUNICATION)

        result = ant.to_dict()

        expected_keys = {
            'id', 'birth_time', 'death_time', 'is_alive', 'age_seconds',
            'remaining_life_seconds', 'state', 'assigned_to',
            'assignment_time'
        }
        assert set(result.keys()) == expected_keys
        assert result['state'] == 'assigned'
        assert result['assigned_to'] == 'S01_COM'