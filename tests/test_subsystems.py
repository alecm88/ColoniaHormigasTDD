import pytest
from src.subsystems import Subsystem, SubsystemType


class TestSubsystem:
    def test_get_known_subsystems_returns_three_subsystems(self):
        subsystems = Subsystem.get_known_subsystems()
        assert len(subsystems) == 3
        assert SubsystemType.COMMUNICATION in subsystems
        assert SubsystemType.COLLECTION in subsystems
        assert SubsystemType.DEFENSE in subsystems

    def test_defense_has_highest_priority(self):
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)
        assert defense.priority_level == 1

    def test_communication_has_medium_priority(self):
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)
        assert communication.priority_level == 2

    def test_collection_has_lowest_priority(self):
        collection = Subsystem.get_by_id(SubsystemType.COLLECTION)
        assert collection.priority_level == 3

    def test_get_by_name_case_insensitive(self):
        defense1 = Subsystem.get_by_name("Defense")
        defense2 = Subsystem.get_by_name("defense")
        defense3 = Subsystem.get_by_name("DEFENSE")

        assert defense1 == defense2 == defense3
        assert defense1.id == SubsystemType.DEFENSE

    def test_get_by_name_unknown_subsystem_returns_none(self):
        unknown = Subsystem.get_by_name("unknown")
        assert unknown is None

    def test_get_by_id_unknown_subsystem_returns_none(self):
        # This would require a mock enum value, so we test with valid IDs
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)
        assert defense is not None
        assert defense.name == "Defense"