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
        assert ant.lifespan == 90

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
        expected_keys = {'id', 'birth_time', 'is_alive', 'age_seconds'}
        assert set(result.keys()) == expected_keys
        assert result['id'] == ant.id
        assert result['is_alive'] == ant.is_alive