from behave import *


@when(u'calling openremote-cli -V')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run openremote-cli -V"
    )


@then(u'should show version')
def step_impl(context):
    assert "openremote-cli version: " in context.response


@when(u'calling openremote-cli without arguments')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run openremote-cli"
    )


@then(u'it should show help')
def step_impl(context):
    assert "usage: openremote-cli" in context.response
    assert "error: unrecognized arguments" not in context.response


@when(u'calling openremote-cil deploy -d')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run openremote-cli deploy -d"
    )


@then(u'should be the same as openremote-cli --dry-run deploy')
def step_impl(context):
    assert "dry-run active!" in context.response
