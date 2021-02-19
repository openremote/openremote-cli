from behave import *


@when(u'calling openremote-cli -v')
def step_impl(context):
    response_code, output = context.execute(f"poetry run openremote-cli -v")
    context.response = output


@then(u'should be the same as openremote-cli')
def step_impl(context):
    assert "usage: openremote-cli" in context.response
