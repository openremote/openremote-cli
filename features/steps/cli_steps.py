from behave import *


@when(u'calling openremote-cli -v')
def step_impl(context):
    response_code, output = context.execute(f"poetry run openremote-cli -v")
    context.response = output


@then(u'should be the same as openremote-cli')
def step_impl(context):
    assert "usage: openremote-cli" in context.response
    assert "error: unrecognized arguments" not in context.response


@when(u'calling openremote-cil deploy -d')
def step_impl(context):
    response_code, output = context.execute(
        f"poetry run openremote-cli deploy -d"
    )
    context.response = output


@then(u'should be the same as openremote-cli --dry-run deploy')
def step_impl(context):
    assert "dry-run active!" in context.response
