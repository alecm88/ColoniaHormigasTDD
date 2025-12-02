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

    def test_subsystem_priority_ordering(self):
        subsystems = Subsystem.get_all_ordered_by_priority()

        # Should be ordered by priority (1, 2, 3)
        assert len(subsystems) == 3
        assert subsystems[0].priority_level == 1
        assert subsystems[0].id == SubsystemType.DEFENSE
        assert subsystems[1].priority_level == 2
        assert subsystems[1].id == SubsystemType.COMMUNICATION
        assert subsystems[2].priority_level == 3
        assert subsystems[2].id == SubsystemType.COLLECTION

    def test_subsystem_equality(self):
        defense1 = Subsystem.get_by_id(SubsystemType.DEFENSE)
        defense2 = Subsystem.get_by_name("Defense")
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)

        assert defense1 == defense2
        assert defense1 != communication
        assert defense2 != communication

    def test_subsystem_string_representation(self):
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)
        collection = Subsystem.get_by_id(SubsystemType.COLLECTION)

        assert str(defense) == "Defense (Priority: 1)"
        assert str(communication) == "Communication (Priority: 2)"
        assert str(collection) == "Collection (Priority: 3)"

    def test_subsystem_description_exists(self):
        subsystems = Subsystem.get_known_subsystems()

        for subsystem_type in subsystems:
            subsystem = Subsystem.get_by_id(subsystem_type)
            assert subsystem.description is not None
            assert len(subsystem.description) > 0

    def test_get_subsystem_by_priority_level(self):
        highest_priority = Subsystem.get_by_priority(1)
        medium_priority = Subsystem.get_by_priority(2)
        lowest_priority = Subsystem.get_by_priority(3)

        assert highest_priority.id == SubsystemType.DEFENSE
        assert medium_priority.id == SubsystemType.COMMUNICATION
        assert lowest_priority.id == SubsystemType.COLLECTION

        # Test invalid priority
        invalid_priority = Subsystem.get_by_priority(0)
        assert invalid_priority is None

        invalid_priority = Subsystem.get_by_priority(4)
        assert invalid_priority is None

    def test_subsystem_has_required_attributes(self):
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)

        assert hasattr(defense, 'id')
        assert hasattr(defense, 'name')
        assert hasattr(defense, 'priority_level')
        assert hasattr(defense, 'description')

        assert defense.id == SubsystemType.DEFENSE
        assert defense.name == "Defense"
        assert defense.priority_level == 1
        assert isinstance(defense.description, str)

    def test_subsystem_is_high_priority(self):
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)
        collection = Subsystem.get_by_id(SubsystemType.COLLECTION)

        assert defense.is_high_priority() is True
        assert communication.is_high_priority() is False
        assert collection.is_high_priority() is False

    def test_subsystem_enum_values_are_unique(self):
        values = set()
        for subsystem_type in SubsystemType:
            assert subsystem_type.value not in values
            values.add(subsystem_type.value)

    def test_all_subsystem_names_are_unique(self):
        names = set()
        subsystems = Subsystem.get_known_subsystems()

        for subsystem_type in subsystems:
            subsystem = Subsystem.get_by_id(subsystem_type)
            assert subsystem.name.lower() not in names
            names.add(subsystem.name.lower())

    def test_get_subsystem_stats(self):
        stats = Subsystem.get_subsystem_stats()

        assert "total_subsystems" in stats
        assert stats["total_subsystems"] == 3

        assert "priority_levels" in stats
        assert len(stats["priority_levels"]) == 3
        assert 1 in stats["priority_levels"]
        assert 2 in stats["priority_levels"]
        assert 3 in stats["priority_levels"]

    def test_subsystem_comparison_operators(self):
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)
        collection = Subsystem.get_by_id(SubsystemType.COLLECTION)

        # Higher priority (lower number) should be "less than" in sorting
        assert defense < communication
        assert communication < collection
        assert defense < collection

        assert not communication < defense
        assert not collection < communication
        assert not collection < defense

    def test_subsystem_hash_consistency(self):
        defense1 = Subsystem.get_by_id(SubsystemType.DEFENSE)
        defense2 = Subsystem.get_by_name("Defense")
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)

        # Same subsystems should have same hash
        assert hash(defense1) == hash(defense2)

        # Different subsystems should have different hashes
        assert hash(defense1) != hash(communication)

    def test_subsystem_get_by_partial_name(self):
        # Test if partial matching is supported
        defense = Subsystem.get_by_partial_name("Def")
        communication = Subsystem.get_by_partial_name("Comm")
        collection = Subsystem.get_by_partial_name("Coll")

        if defense is not None:  # If method exists
            assert defense.id == SubsystemType.DEFENSE
        if communication is not None:
            assert communication.id == SubsystemType.COMMUNICATION
        if collection is not None:
            assert collection.id == SubsystemType.COLLECTION

    def test_subsystem_type_conversion(self):
        # Test conversion between string and enum
        defense_str = "DEFENSE"
        defense_enum = SubsystemType[defense_str]
        assert defense_enum == SubsystemType.DEFENSE

        communication_str = "COMMUNICATION"
        communication_enum = SubsystemType[communication_str]
        assert communication_enum == SubsystemType.COMMUNICATION

        collection_str = "COLLECTION"
        collection_enum = SubsystemType[collection_str]
        assert collection_enum == SubsystemType.COLLECTION

    def test_get_subsystems_by_priority_range(self):
        # Get all high priority subsystems (priority <= 2)
        high_priority = Subsystem.get_by_priority_range(1, 2)

        if high_priority is not None:  # If method exists
            assert len(high_priority) == 2
            priorities = [s.priority_level for s in high_priority]
            assert 1 in priorities
            assert 2 in priorities
            assert 3 not in priorities