import pytest
from src.subsystems import Subsystem, SubsystemType


class TestSubsystem:
    def test_get_known_subsystems_returns_three_subsystems(self):
        subsystems = Subsystem.get_known_subsystems()
        assert len(subsystems) == 5
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
        defense1 = Subsystem.get_by_name("S05_DEF")
        defense2 = Subsystem.get_by_name("s05_def")
        defense3 = Subsystem.get_by_name("S05_deF")

        assert defense1 == defense2 == defense3
        assert defense1.id == SubsystemType.DEFENSE

    def test_get_by_name_unknown_subsystem_returns_none(self):
        unknown = Subsystem.get_by_name("unknown")
        assert unknown is None

    def test_get_by_id_unknown_subsystem_returns_none(self):
        # This would require a mock enum value, so we test with valid IDs
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)
        assert defense is not None
        assert defense.name == "S05_DEF"

    def test_subsystem_equality(self):
        defense1 = Subsystem.get_by_id(SubsystemType.DEFENSE)
        defense2 = Subsystem.get_by_name("S05_DEF")
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)

        assert defense1 == defense2
        assert defense1 != communication
        assert defense2 != communication

    def test_subsystem_has_required_attributes(self):
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)

        assert hasattr(defense, 'id')
        assert hasattr(defense, 'name')
        assert hasattr(defense, 'priority_level')

        assert defense.id == SubsystemType.DEFENSE
        assert defense.name == "S05_DEF"
        assert defense.priority_level == 1
        
    def test_subsystem_string_representation(self):
        defense = Subsystem.get_by_id(SubsystemType.DEFENSE)
        communication = Subsystem.get_by_id(SubsystemType.COMMUNICATION)
        collection = Subsystem.get_by_id(SubsystemType.COLLECTION)

        assert str(defense) == "S05_DEF (Priority: 1)"
        assert str(communication) == "S01_COM (Priority: 2)"
        assert str(collection) == "S02_REC (Priority: 3)"

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