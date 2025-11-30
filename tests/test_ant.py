import pytest
from datetime import datetime, timedelta
from src.ant import Ant


class TestAnt:
    def test_ant_creation(self):
        ant = Ant()
        assert ant.id is not None
        assert isinstance(ant.birth_time, datetime)
        assert ant.is_alive is True

    def test_ant_lifespan_is_90_seconds(self):
        ant = Ant()
        assert ant.lifespan_seconds == 90

    def test_ant_is_5_seconds_old (self):
        ant = Ant()
        # Simulate 5 seconds passing
        ant.birth_time = datetime.now() - timedelta(seconds=5)
        assert ant.age_seconds >= 4.99 and ant.age_seconds <= 5.01

    def test_ant_lifespan_after_5_seconds (self):
        ant = Ant()
        # Simulate 5 seconds passing
        ant.birth_time = datetime.now() - timedelta(seconds=5)
        assert ant.remaining_life_seconds == 85

    def test_ant_dies_after_90_seconds(self):
        ant = Ant()
        # Simulate 91 seconds passing
        ant.birth_time = datetime.now() - timedelta(seconds=91)
        assert ant.is_alive is False

    def test_ant_is_alive_before_90_seconds(self):
        ant = Ant()
        # Simulate 89 seconds passing
        ant.birth_time = datetime.now() - timedelta(seconds=89)
        assert ant.is_alive is True

    def test_ant_has_unique_id(self):
        ant1 = Ant()
        ant2 = Ant()
        assert ant1.id != ant2.id

    def test_ant_to_dict(self):
        ant = Ant()
        result = ant.to_dict()
        expected_keys = {'id', 'birth_time', 'death_time', 'is_alive', 'age_seconds', 'remaining_life_seconds', 'state', 'assigned_to', 'assignment_time'}
        assert set(result.keys()) == expected_keys
        assert result['id'] == ant.id
        assert result['is_alive'] == ant.is_alive
    
    def test_ant_death_time (self):
        ant = Ant()
        assert ant.death_time == datetime.now() + timedelta(seconds=90)

    def test_ant_is_available (self):
        ant = Ant()
        assert ant.is_available_for_assignment == True

    def test_dead_ant_is_available (self):
        ant = Ant()
        # Simulate 91 seconds passing
        ant.birth_time = datetime.now() - timedelta(seconds=91)
        assert ant.is_available_for_assignment == False
        
    def test_assign_ant_to_subsystem (self):
        ant = Ant()
        ant.assign_to_subsystem('Test')
        assert ant.assigned_to == 'Test'

    def test_assigned_ant_is_available (self):
        ant = Ant()
        ant.assign_to_subsystem('Test')
        assert ant.is_available_for_assignment == False

    def test_assign_ant_to_two_subsystems (self):
        ant = Ant()
        ant.assign_to_subsystem('Test')
        ant.assign_to_subsystem('Test2')
        assert ant.assigned_to == 'Test'

    def test_assign_ant_to_two_subsystems_with_return (self):
        ant = Ant()
        ant.assign_to_subsystem('Test')
        ant.return_from_assignment()
        ant.assign_to_subsystem('Test2')
        assert ant.assigned_to == 'Test2'

    def test_ant_died_on_assignment (self):
        ant = Ant()
        ant.assign_to_subsystem('Test')
        ant.return_from_assignment(True)
        assert ant.is_alive == False