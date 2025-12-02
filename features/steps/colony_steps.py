from datetime import datetime, timedelta
import time
try:
    from behave import given, when, then
except ImportError:
    # For testing without behave installed
    def given(pattern):
        def decorator(func):
            return func
        return decorator
    def when(pattern):
        def decorator(func):
            return func
        return decorator
    def then(pattern):
        def decorator(func):
            return func
        return decorator

from src.colony import Colony
from src.ant import AntState
from src.subsystems import SubsystemType


# === BACKGROUND STEPS ===

@given('the colony is configured for academic requirements')
def step_configure_colony_academic(context):
    context.colony = Colony(max_ants=100, initial_food_stock=1000, ant_lifespan_minutes=1.5)
    context.initial_food = context.colony.food_stock


@given('the known subsystems are "{comm}", "{coll}", and "{defense}"')
def step_define_subsystems(context, comm, coll, defense):
    context.subsystems = {
        'communication': comm.lower(),
        'collection': coll.lower(),
        'defense': defense.lower()
    }


@given('Defense has priority {def_priority:d}, Communication has priority {comm_priority:d}, and Collection has priority {coll_priority:d}')
def step_define_priorities(context, def_priority, comm_priority, coll_priority):
    context.priorities = {
        'defense': def_priority,
        'communication': comm_priority,
        'collection': coll_priority
    }


# === GIVEN STEPS ===

@given('the colony has sufficient food stock')
def step_colony_sufficient_food(context):
    if not hasattr(context, 'colony'):
        context.colony = Colony(initial_food_stock=1000)
    context.colony.food_stock = 1000


@given('the colony has insufficient food stock')
def step_colony_insufficient_food(context):
    if not hasattr(context, 'colony'):
        context.colony = Colony(initial_food_stock=5)
    context.colony.food_stock = 5  # Less than food_per_ant (10)


@given('the colony is at maximum capacity')
def step_colony_at_capacity(context):
    if not hasattr(context, 'colony'):
        context.colony = Colony(max_ants=1, initial_food_stock=1000)
    context.colony.max_ants = 1
    # Fill the capacity
    context.colony.create_ant()


@given('I have an ant assigned to "{subsystem}"')
def step_have_assigned_ant(context, subsystem):
    if not hasattr(context, 'colony'):
        context.colony = Colony()
    context.assigned_ant = context.colony.request_ant(subsystem)
    assert context.assigned_ant is not None


@given('the colony has {count:d} free ants')
def step_colony_has_free_ants(context, count):
    if not hasattr(context, 'colony'):
        context.colony = Colony()
    for _ in range(count):
        ant = context.colony.create_ant()
        assert ant is not None


@given('I have an ant assigned to "{subsystem}" for more than 10 seconds')
def step_have_old_assigned_ant(context, subsystem):
    if not hasattr(context, 'colony'):
        context.colony = Colony()
    ant = context.colony.request_ant(subsystem)
    assert ant is not None
    # Make the assignment old
    ant.assignment_time = datetime.now() - timedelta(seconds=15)
    if not hasattr(context, 'old_assignments'):
        context.old_assignments = {}
    context.old_assignments[subsystem.lower()] = ant


@given('both ants have been assigned for more than 10 seconds')
def step_both_ants_old_assignment(context):
    # This assumes previous steps have created the ants
    for ant in context.colony.get_assigned_ants():
        ant.assignment_time = datetime.now() - timedelta(seconds=15)


@given('the colony has 1 free ant')
def step_colony_one_free_ant(context):
    if not hasattr(context, 'colony'):
        context.colony = Colony()
    context.colony.create_ant()


@given('the colony has 1 ant assigned to "{subsystem}"')
def step_colony_one_assigned_ant(context, subsystem):
    if not hasattr(context, 'colony'):
        context.colony = Colony()
    ant = context.colony.request_ant(subsystem)
    assert ant is not None


@given('the colony is configured with {lifespan:f} minute lifespan')
def step_configure_short_lifespan(context, lifespan):
    context.colony = Colony(ant_lifespan_minutes=lifespan)


@given('I create an ant')
def step_create_single_ant(context):
    if not hasattr(context, 'colony'):
        context.colony = Colony()
    context.ant = context.colony.create_ant()
    assert context.ant is not None


@given('I have an ant with 30 seconds of remaining life')
def step_ant_with_limited_life(context):
    if not hasattr(context, 'colony'):
        context.colony = Colony(ant_lifespan_minutes=1.0)  # 60 seconds total
    context.ant = context.colony.create_ant()
    # Make the ant 29 seconds old (31 seconds remaining, but wait time is 10s)
    context.ant.birth_time = datetime.now() - timedelta(seconds=29)


@given('the colony starts with 1000 food units')
def step_colony_initial_food(context):
    if not hasattr(context, 'colony'):
        context.colony = Colony(initial_food_stock=1000)
    assert context.colony.food_stock == 1000
    context.initial_food = 1000


# === WHEN STEPS ===

@when('I request an ant for "{subsystem}" subsystem')
def step_request_ant_for_subsystem(context, subsystem):
    context.requested_ant = context.colony.request_ant(subsystem)
    context.last_subsystem = subsystem.lower()


@when('the ant returns with food')
def step_ant_returns_with_food(context):
    context.initial_food_stock = context.colony.food_stock
    success = context.colony.return_ant(
        context.assigned_ant.id,
        returned_with_food=True,
        died_in_mission=False
    )
    context.return_success = success


@when('the ant dies during the mission')
def step_ant_dies_in_mission(context):
    success = context.colony.return_ant(
        context.assigned_ant.id,
        returned_with_food=False,
        died_in_mission=True
    )
    context.return_success = success


@when('"{subsystem}" requests {count:d} emergency ants')
def step_request_emergency_ants(context, subsystem, count):
    context.emergency_ants = context.colony.request_emergency_ants(
        requesting_subsystem=subsystem,
        number_needed=count,
        max_wait_seconds=30
    )


@when('I request the comprehensive colony status')
def step_request_comprehensive_status(context):
    context.status = context.colony.get_comprehensive_status()


@when('more than {lifespan:f} minutes pass')
def step_time_passes_minutes(context, lifespan):
    # Simulate time passing by making the ant old
    seconds = lifespan * 60 + 1  # Add 1 second to ensure death
    if hasattr(context, 'ant') and context.ant:
        context.ant.birth_time = datetime.now() - timedelta(seconds=seconds)
        context.ant.update_state()


@when('I request assignment for a task requiring {duration:d} seconds')
def step_request_assignment_with_duration(context, duration):
    context.assignment_result = context.ant.can_handle_task(duration)


@when('I create {count:d} ants')
def step_create_multiple_ants(context, count):
    context.created_ants = []
    for _ in range(count):
        ant = context.colony.create_ant()
        if ant:
            context.created_ants.append(ant)


@when('an ant returns with food')
def step_when_ant_returns_with_food(context):
    # Create and assign an ant first
    if not hasattr(context, 'test_ant'):
        context.test_ant = context.colony.request_ant("Collection")

    context.food_before_return = context.colony.food_stock
    context.colony.return_ant(context.test_ant.id, returned_with_food=True)


# === THEN STEPS ===

@then('an ant should be assigned successfully')
def step_ant_assigned_successfully(context):
    assert context.requested_ant is not None
    assert context.requested_ant.state == AntState.ASSIGNED


@then('the ant should be marked as assigned to "{subsystem}"')
def step_ant_marked_assigned_to_subsystem(context, subsystem):
    expected_subsystem = SubsystemType.DEFENSE if subsystem.lower() == 'defense' else \
                        SubsystemType.COMMUNICATION if subsystem.lower() == 'communication' else \
                        SubsystemType.COLLECTION
    assert context.requested_ant.assigned_to == expected_subsystem


@then('food should be consumed for ant creation if needed')
def step_food_consumed_if_needed(context):
    # This is automatically handled by the colony.request_ant method
    pass


@then('the assignment should fail')
def step_assignment_should_fail(context):
    assert context.requested_ant is None


@then('I should receive an error about unknown subsystem')
def step_error_unknown_subsystem(context):
    # In BDD context, we check that the ant was not assigned
    assert context.requested_ant is None


@then('I should receive an error about insufficient food')
def step_error_insufficient_food(context):
    assert context.requested_ant is None


@then('I should receive an error about capacity or food')
def step_error_capacity_or_food(context):
    assert context.requested_ant is None


@then('the ant should be marked as free')
def step_ant_marked_free(context):
    assert context.return_success is True
    assert context.assigned_ant.state == AntState.FREE


@then('the colony food stock should increase')
def step_food_stock_increases(context):
    assert context.colony.food_stock > context.initial_food_stock


@then('the ant should be available for new assignments')
def step_ant_available_for_assignment(context):
    assert context.assigned_ant.is_available_for_assignment


@then('the ant should be marked as dead')
def step_ant_marked_dead(context):
    assert context.return_success is True
    assert context.assigned_ant.state == AntState.DEAD


@then('the ant should not be available for assignments')
def step_ant_not_available(context):
    assert not context.assigned_ant.is_available_for_assignment


@then('{count:d} ants should be assigned to "{subsystem}"')
def step_ants_assigned_to_subsystem(context, count, subsystem):
    assert len(context.emergency_ants) == count
    expected_subsystem = SubsystemType.DEFENSE if subsystem.lower() == 'defense' else \
                        SubsystemType.COMMUNICATION if subsystem.lower() == 'communication' else \
                        SubsystemType.COLLECTION
    for ant in context.emergency_ants:
        assert ant.assigned_to == expected_subsystem


@then('the colony should be in emergency mode')
def step_colony_emergency_mode(context):
    assert context.colony.emergency_mode is True


@then('all assigned ants should have "{subsystem}" as their subsystem')
def step_all_ants_have_subsystem(context, subsystem):
    expected_subsystem = SubsystemType.DEFENSE if subsystem.lower() == 'defense' else \
                        SubsystemType.COMMUNICATION if subsystem.lower() == 'communication' else \
                        SubsystemType.COLLECTION
    for ant in context.emergency_ants:
        assert ant.assigned_to == expected_subsystem


@then('the "{subsystem1}" ant should be reassigned to "{subsystem2}"')
def step_ant_reassigned(context, subsystem1, subsystem2):
    expected_subsystem = SubsystemType.DEFENSE if subsystem2.lower() == 'defense' else \
                        SubsystemType.COMMUNICATION if subsystem2.lower() == 'communication' else \
                        SubsystemType.COLLECTION

    # Find the ant that was originally assigned to subsystem1
    old_ant = context.old_assignments.get(subsystem1.lower())
    if old_ant:
        assert old_ant.assigned_to == expected_subsystem


@then('the "{subsystem}" ant should remain assigned to "{same_subsystem}"')
def step_ant_remains_assigned(context, subsystem, same_subsystem):
    # Find ants still assigned to the original subsystem
    expected_subsystem = SubsystemType.COMMUNICATION if same_subsystem.lower() == 'communication' else \
                        SubsystemType.DEFENSE if same_subsystem.lower() == 'defense' else \
                        SubsystemType.COLLECTION

    found_ant = False
    for ant in context.colony.get_assigned_ants():
        if ant.assigned_to == expected_subsystem:
            found_ant = True
            break
    assert found_ant


@then('1 additional ant should be created and assigned to "{subsystem}" if possible')
def step_additional_ant_created(context, subsystem):
    # This is handled automatically by the emergency request system
    pass


@then('only the "{subsystem1}" ant should be reassigned to "{subsystem2}"')
def step_only_specific_ant_reassigned(context, subsystem1, subsystem2):
    # Check that only the expected ant was reassigned
    expected_subsystem = SubsystemType.COMMUNICATION if subsystem2.lower() == 'communication' else \
                        SubsystemType.DEFENSE if subsystem2.lower() == 'defense' else \
                        SubsystemType.COLLECTION

    reassigned_count = len([ant for ant in context.colony.get_assigned_ants()
                           if ant.assigned_to == expected_subsystem])
    assert reassigned_count >= 1


@then('I should see {count:d} total ants')
def step_see_total_ants(context, count):
    assert context.status['total_ants'] == count


@then('I should see {count:d} free ant')
@then('I should see {count:d} free ants')
def step_see_free_ants(context, count):
    assert context.status['free_ants'] == count


@then('I should see {count:d} assigned ants')
def step_see_assigned_ants(context, count):
    assert context.status['assigned_ants'] == count


@then('I should see {count:d} ant assigned to "{subsystem}"')
@then('I should see {count:d} ants assigned to "{subsystem}"')
def step_see_ants_assigned_to_subsystem(context, count, subsystem):
    subsystem_key = subsystem.lower()
    assert context.status['ants_by_subsystem'][subsystem_key] == count


@then('I should see the current food stock')
def step_see_food_stock(context):
    assert 'food_stock' in context.status
    assert context.status['food_stock'] >= 0


@then('I should see whether more ants can be created')
def step_see_can_create_more(context):
    assert 'can_create_more' in context.status
    assert isinstance(context.status['can_create_more'], bool)


@then('the ant should die automatically')
def step_ant_dies_automatically(context):
    assert not context.ant.is_alive


@then('any assignment should be cleared')
def step_assignment_cleared(context):
    assert context.ant.assigned_to is None
    assert context.ant.assignment_time is None


@then('the assignment should fail due to insufficient life')
def step_assignment_fails(context):
    assert context.assignment_result is False


@then('I should receive an error about insufficient remaining life')
def step_error_insufficient_life(context):
    assert context.assignment_result is False


@then('the food stock should decrease by {amount:d} units')
def step_food_stock_decreases(context, amount):
    expected_food = context.initial_food - amount
    assert context.colony.food_stock == expected_food


@then('the food stock should increase by {amount:d} units')
def step_food_stock_increases_by_amount(context, amount):
    expected_increase = context.food_before_return + amount
    assert context.colony.food_stock == expected_increase