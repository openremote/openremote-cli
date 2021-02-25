from behave import *


@when(u'calling openremote-cli -V')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run openremote-cli -V"
    )


@then(u'should show version')
def step_impl(context):
    assert "openremote-cli/" in context.response


@when(u'calling openremote-cli without arguments')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run openremote-cli --no-telemetry"
    )


@then(u'it should show help')
def step_impl(context):
    assert "usage: openremote-cli" in context.response
    assert "error: unrecognized arguments" not in context.response
