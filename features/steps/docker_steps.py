from behave import *


@given(u'we have docker installed')
def step_impl(context):
    response_code, output = context.execute('docker -v')
    assert response_code == 0


@when(u'docker run --rm -ti openremote/openremote-cli -V')
def step_impl(context):
    response_code, context.output = context.execute(
        f"docker run --rm openremote/openremote-cli -V --no-telemetry"
    )
    assert response_code == 0
    print(context.output)


@then(u'there should be openremote-cli version response')
def step_impl(context):
    assert "openremote-cli/" in context.output
