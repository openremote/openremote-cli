import os

from openremote_cli import config


@given(u'we have SETUP_ADMIN_PASSWORD variable set')
def step_impl(context):
    context.password = os.environ['SETUP_ADMIN_PASSWORD']


@when(u'login into demo.openremote.io as admin')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli manager --login -v -t'
    )
    assert context.code == 0
    print(context.output)


@then(u'a token is fetched stored in config')
def step_impl(context):
    # Check if we have some juice from it
    assert len(config.get_token('demo.openremote.io')) > 100


@then(u'we can list realms')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli manager --list-realms -q -t'
    )
    print(context.output)
    assert context.code == 0
    assert 'master' in context.output


@then(u'we can list users of master realm')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli manager --list-users -q -t'
    )
    print(context.output)
    assert context.code == 0
    assert 'master' in context.output


@then(u'we can list public assets from master realm')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli manager --list-public-assets -q -t'
    )
    print(context.output)
    assert context.code == 0


@when(u'using alias sso for staging.demo.openremote.io')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run or sso --open --quit --quiet --no-telemetry -d staging.demo.openremote.io'
    )


@then(u'there should be no errors')
def step_impl(context):
    assert context.code == 0


@when(u'login into demo realm smartcity as user smartcity')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli sso -t -o -p smartcity -u smartcity --realm smartcity --quit -q'
    )


@when(u'running manager --test-http-test')
def step_impl(context):
    raise NotImplementedError(u'STEP: When running manager --test-http-test')
