import pytest
from datetime import datetime, timedelta
from src.colony import Colony
from src.ant import Ant


class TestColony:
    def test_colony_creation_with_max_ants(self):
        colony = Colony(max_ants=5)
        assert colony.max_ants == 5
        assert len(colony.ants) == 0

    def test_create_ant_when_under_limit(self):
        colony = Colony(max_ants=2)
        ant = colony.create_ant()
        assert ant is not None
        assert len(colony.ants) == 1
        assert ant.id in colony.ants

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

    def test_can_create_ant_after_cleanup(self):
        colony = Colony(max_ants=1)
        ant = colony.create_ant()

        # Make ant die
        colony.ants[ant.id].birth_time = datetime.now() - timedelta(seconds=91)
        colony.cleanup_dead_ants()

        # Should be able to create new ant now
        new_ant = colony.create_ant()
        assert new_ant is not None
        assert len(colony.ants) == 1

    def test_get_alive_ants(self):
        colony = Colony(max_ants=3)
        ant1 = colony.create_ant()
        ant2 = colony.create_ant()

        # Make one ant die
        colony.ants[ant1.id].birth_time = datetime.now() - timedelta(seconds=91)

        alive_ants = colony.get_alive_ants()
        assert len(alive_ants) == 1
        assert alive_ants[0].id == ant2.id

    def test_get_colony_status(self):
        colony = Colony(max_ants=5)
        colony.create_ant()
        colony.create_ant()

        status = colony.get_status()
        expected_keys = {'total_ants', 'alive_ants', 'dead_ants', 'max_ants', 'can_create_more'}
        assert set(status.keys()) == expected_keys
        assert status['total_ants'] == 2
        assert status['alive_ants'] == 2
        assert status['dead_ants'] == 0
        assert status['max_ants'] == 5
        assert status['can_create_more'] is True