Feature: Ant Colony Management
  As a colony manager
  I want to manage a population of ants with limited capacity
  So that I can control the ant ecosystem

  Background:
    Given the colony is configured with a maximum of 3 ants

  Scenario: Creating a new ant when colony has capacity
    Given the colony has 2 alive ants
    When I create a new ant
    Then the ant should be created successfully
    And the colony should have 3 alive ants

  Scenario: Cannot create ant when colony is at capacity
    Given the colony has 3 alive ants
    When I try to create a new ant
    Then the ant creation should fail
    And the colony should still have 3 alive ants

  Scenario: Ants die after 90 seconds
    Given I create an ant
    When 91 seconds pass
    Then the ant should be dead
    And the colony should have 0 alive ants

  Scenario: Dead ants are automatically cleaned up when creating new ants
    Given the colony has 3 alive ants
    And all ants are older than 90 seconds
    When I create a new ant
    Then the ant should be created successfully
    And the colony should have 1 alive ant

  Scenario: Get colony status
    Given the colony has 2 alive ants
    When I request the colony status
    Then I should see 2 alive ants
    And I should see maximum capacity is 3
    And I should see that more ants can be created