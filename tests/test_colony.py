import pytest
from datetime import datetime, timedelta
from src.colony import Colony
from src.ant import Ant


class TestColony:
    def test_colony_creation_with_max_ants(self):
        colony = Colony(max_ants=5, initial_food_stock=1000)
        assert colony.max_ants == 5
        assert colony.food_stock == 1000
        # assert len(colony.ants) == 0

    def test_create_ant_when_under_limit(self):
        colony = Colony(max_ants=2)
        currentFood = colony.food_stock
        ant = colony.create_ant()
        assert ant is not None
        assert len(colony.ants) == 1
        assert ant.id in colony.ants
        assert colony.food_stock == (currentFood - colony.food_per_ant)

    def test_cannot_create_ant_without_food(self):
        colony = Colony(max_ants=2, initial_food_stock=5, food_per_ant=10)
        ant = colony.create_ant()
        assert ant is None
        assert len(colony.ants) == 0
        assert colony.food_stock == 5  # Unchanged

    def test_cannot_create_ant_when_at_limit(self):
        colony = Colony(max_ants=1)
        colony.create_ant()
        ant2 = colony.create_ant()
        assert ant2 is None
        assert len(colony.ants) == 1

    def test_cleanup_dead_ants(self):
        colony = Colony(max_ants=3)
        ant = colony.create_ant()
        # Make ant die by setting old birth time
        colony.ants[ant.id].birth_time = datetime.now() - timedelta(seconds=91)

        colony.cleanup_dead_ants()
        assert len(colony.ants) == 0

    def test_can_create_ant_after_death(self):
        colony = Colony(max_ants=1)
        ant = colony.create_ant()

        # Make ant die
        colony.ants[ant.id].birth_time = datetime.now() - timedelta(seconds=91)

        # Should be able to create new ant now
        new_ant = colony.create_ant()
        assert new_ant is not None
        assert len(colony.ants) == 1

    def test_get_alive_ants(self):
        colony = Colony(max_ants=3)
        ant1 = colony.create_ant()
        ant2 = colony.create_ant()
        ant3 = colony.create_ant()

        # Make one ant die
        colony.ants[ant1.id].birth_time = datetime.now() - timedelta(seconds=91)
        colony.ants[ant2.id].return_from_assignment(died_in_mission=True)

        alive_ants = colony.get_alive_ants()
        assert len(alive_ants) == 1
        assert alive_ants[0].id == ant3.id

    def test_assign_ant(self):
        colony = Colony(max_ants=3)
        ant1 = colony.create_ant()

        # Send ant on a mission
        colony.ants[ant1.id].assign_to_subsystem('Test')

        assert ant1.assigned_to == 'Test'
        assert ant1.state.value == 'assigned'

    def test_get_assigned_and_free_ants(self):
        colony = Colony(max_ants=3)
        ant1 = colony.create_ant()
        ant2 = colony.create_ant()
        ant3 = colony.create_ant()

        # Send ant on a mission
        colony.ants[ant1.id].assign_to_subsystem('Test')

        assigned_ants = colony.get_assigned_ants()
        free_ants = colony.get_free_ants()
        assert len(assigned_ants) == 1
        assert len(free_ants) == 2

    def test_get_colony_status(self):
        colony = Colony(max_ants=5, initial_food_stock=100, food_per_ant=10)
        colony.create_ant()
        colony.create_ant()
        assignedAnt = colony.create_ant()
        deadAnt = colony.create_ant()
        
        colony.ants[deadAnt.id].birth_time = datetime.now() - timedelta(seconds=91)
        colony.ants[assignedAnt.id].assign_to_subsystem('Test')

        status = colony.get_status()
        expected_keys = {'total_ants', 'alive_ants', 'free_ants', 'assigned_ants', 'dead_ants', 'max_ants', 'food_stock'}
        assert set(status.keys()) == expected_keys
        assert status['total_ants'] == 4
        assert status['alive_ants'] == 3
        assert status['free_ants'] == 2
        assert status['assigned_ants'] == 1
        assert status['dead_ants'] == 1
        assert status['max_ants'] == 5
        assert status['food_stock'] == 60

    def test_get_ant_by_id(self):
        colony = Colony(max_ants=2)
        ant = colony.create_ant()

        ant2 = colony.get_ant_by_id(ant.id)

        assert ant is not None
        assert len(colony.ants) == 1
        assert ant.id in colony.ants
        assert ant.id == ant2.id

    def test_get_ant_by_invalid_id(self):
        colony = Colony(max_ants=2)
        ant = colony.create_ant()

        ant2 = colony.get_ant_by_id('invalidid')

        assert ant is not None
        assert len(colony.ants) == 1
        assert ant.id in colony.ants
        assert ant2 is None

    def test_colony_reset(self):
        colony = Colony(max_ants=3, initial_food_stock=100)
        colony.create_ant()
        colony.create_ant()

        colony.reset_colony()

        assert len(colony.ants) == 0
        assert colony.food_stock == 100