Feature: Queen Ant Subsystem - Ant Assignment and Management
  As the Queen Ant subsystem
  I want to manage ant assignments to different subsystems
  So that the colony can efficiently handle different tasks with priority

  Background:
    Given the colony is configured for academic requirements
    And the known subsystems are "Communication", "Collection", and "Defense"
    And Defense has priority 1, Communication has priority 2, and Collection has priority 3

  Scenario: Assign ant to a known subsystem
    Given the colony has sufficient food stock
    When I request an ant for "Defense" subsystem
    Then an ant should be assigned successfully
    And the ant should be marked as assigned to "Defense"
    And food should be consumed for ant creation if needed

  Scenario: Reject assignment to unknown subsystem
    Given the colony has sufficient food stock
    When I request an ant for "UnknownSystem" subsystem
    Then the assignment should fail
    And I should receive an error about unknown subsystem

  Scenario: Cannot assign ant when insufficient food
    Given the colony has insufficient food stock
    When I request an ant for "Collection" subsystem
    Then the assignment should fail
    And I should receive an error about insufficient food

  Scenario: Ant returns successfully with food
    Given I have an ant assigned to "Collection"
    When the ant returns with food
    Then the ant should be marked as free
    And the colony food stock should increase
    And the ant should be available for new assignments

  Scenario: Ant dies during mission
    Given I have an ant assigned to "Defense"
    When the ant dies during the mission
    Then the ant should be marked as dead
    And the ant should not be available for assignments

  Scenario: Emergency ant request with available ants
    Given the colony has 2 free ants
    When "Defense" requests 2 emergency ants
    Then 2 ants should be assigned to "Defense"
    And the colony should be in emergency mode
    And all assigned ants should have "Defense" as their subsystem