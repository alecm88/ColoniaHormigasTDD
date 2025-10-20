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

  Scenario: Cannot assign ant when at capacity and insufficient food
    Given the colony is at maximum capacity
    And the colony has insufficient food stock
    When I request an ant for "Communication" subsystem
    Then the assignment should fail
    And I should receive an error about capacity or food

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

  Scenario: Emergency ant request with reassignment from lower priority
    Given I have an ant assigned to "Collection" for more than 10 seconds
    And I have an ant assigned to "Communication" for more than 10 seconds
    When "Defense" requests 2 emergency ants
    Then the "Collection" ant should be reassigned to "Defense"
    And the "Communication" ant should remain assigned to "Communication"
    And 1 additional ant should be created and assigned to "Defense" if possible

  Scenario: Priority-based reassignment during emergency
    Given I have an ant assigned to "Collection"
    And I have an ant assigned to "Defense"
    And both ants have been assigned for more than 10 seconds
    When "Communication" requests 1 emergency ant
    Then only the "Collection" ant should be reassigned to "Communication"
    And the "Defense" ant should remain with "Defense"

  Scenario: Comprehensive colony status reporting
    Given the colony has 1 free ant
    And the colony has 1 ant assigned to "Defense"
    And the colony has 1 ant assigned to "Communication"
    When I request the comprehensive colony status
    Then I should see 3 total ants
    And I should see 1 free ant
    And I should see 2 assigned ants
    And I should see 1 ant assigned to "Defense"
    And I should see 1 ant assigned to "Communication"
    And I should see 0 ants assigned to "Collection"
    And I should see the current food stock
    And I should see whether more ants can be created

  Scenario: Ant lifespan management
    Given the colony is configured with 0.02 minute lifespan
    And I create an ant
    When more than 0.02 minutes pass
    Then the ant should die automatically
    And the ant should be marked as dead
    And any assignment should be cleared

  Scenario: Task duration validation
    Given I have an ant with 30 seconds of remaining life
    When I request assignment for a task requiring 40 seconds
    Then the assignment should fail
    And I should receive an error about insufficient remaining life

  Scenario: Food stock management
    Given the colony starts with 1000 food units
    When I create 10 ants
    Then the food stock should decrease by 100 units
    And when an ant returns with food
    Then the food stock should increase by 20 units