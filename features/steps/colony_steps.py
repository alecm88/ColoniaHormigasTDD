from datetime import datetime, timedelta
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


@given('the colony is configured with a maximum of {max_ants:d} ants')
def step_configure_colony(context, max_ants):
    context.colony = Colony(max_ants=max_ants)


@given('the colony has {count:d} alive ants')
def step_colony_has_ants(context, count):
    for _ in range(count):
        context.colony.create_ant()


@given('I create an ant')
def step_create_ant(context):
    context.ant = context.colony.create_ant()


@given('all ants are older than 90 seconds')
def step_make_ants_old(context):
    old_time = datetime.now() - timedelta(seconds=91)
    for ant in context.colony.ants.values():
        ant.birth_time = old_time


@when('I create a new ant')
def step_create_new_ant(context):
    context.new_ant = context.colony.create_ant()


@when('I try to create a new ant')
def step_try_create_ant(context):
    context.new_ant = context.colony.create_ant()


@when('{seconds:d} seconds pass')
def step_time_passes(context, seconds):
    # Simulate time passing by modifying the ant's birth time
    if hasattr(context, 'ant') and context.ant:
        context.ant.birth_time = datetime.now() - timedelta(seconds=seconds)


@when('I request the colony status')
def step_request_status(context):
    context.status = context.colony.get_status()


@then('the ant should be created successfully')
def step_ant_created_successfully(context):
    assert context.new_ant is not None
    assert context.new_ant.is_alive


@then('the ant creation should fail')
def step_ant_creation_fails(context):
    assert context.new_ant is None


@then('the colony should have {count:d} alive ants')
def step_check_alive_ants_count(context, count):
    alive_ants = context.colony.get_alive_ants()
    assert len(alive_ants) == count

@then('the colony should have 1 alive ant')
def step_check_one_alive_ant(context):
    alive_ants = context.colony.get_alive_ants()
    assert len(alive_ants) == 1


@then('the colony should still have {count:d} alive ants')
def step_check_still_alive_ants_count(context, count):
    alive_ants = context.colony.get_alive_ants()
    assert len(alive_ants) == count


@then('the ant should be dead')
def step_ant_should_be_dead(context):
    assert not context.ant.is_alive


@then('I should see {count:d} alive ants')
def step_check_status_alive_ants(context, count):
    assert context.status['alive_ants'] == count


@then('I should see maximum capacity is {capacity:d}')
def step_check_status_max_capacity(context, capacity):
    assert context.status['max_ants'] == capacity


@then('I should see that more ants can be created')
def step_check_can_create_more(context):
    assert context.status['can_create_more'] is True