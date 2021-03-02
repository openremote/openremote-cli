from behave import *


@when(u'calling openremote-cli -V')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run openremote-cli -V --no-telemetry"
    )
    assert context.code == 0


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


@given(u'we have aws installed')
def step_impl(context):
    response_code, output = context.execute('aws --version')
    assert response_code == 0


@when(
    u'we call openremote-cli configure-aws --id <id> --secret <secret> -d -v'
)
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli configure_aws --id id --secret secret -n -v --no-telemetry'
    )
    print(context.output)


@then(u'aws configure set profile.openremote-cli.aws_access_key_id <id>')
def step_impl(context):
    assert (
        'aws configure set profile.openremote-cli.aws_access_key_id id'
        in context.output
    )


@then(
    u'aws configure set profile.openremote-cli.aws_secret_access_key <secret>'
)
def step_impl(context):
    assert (
        'aws configure set profile.openremote-cli.aws_secret_access_key secret'
        in context.output
    )


@then(u'aws configure set profile.openremote-cli.region eu-west-1')
def step_impl(context):
    assert (
        'aws configure set profile.openremote-cli.region eu-west-1'
        in context.output
    )


@then(u'ssh-keygen -f openremote -t rsa -b 4096  -C "me@privacy.net"')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then ssh-keygen -f openremote -t rsa -b 4096  -C "me@privacy.net"'
    )


@then(
    u'aws ec2 import-key-pair --key-name openremote --public-key-material fileb://openremote.pub'
)
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then aws ec2 import-key-pair --key-name openremote --public-key-material fileb://openremote.pub'
    )


@then(u'aws ec2 create-default-vpc --profile mvp')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then aws ec2 create-default-vpc --profile mvp'
    )


# Required tools
@when(u'or perquisites -v --dry-run')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run or perquisites -v --dry-run --no-telemetry"
    )
    assert context.code == 0


@then(u'check if all required tools are installed')
def step_impl(context):
    assert "Checking" in context.response


@when(u'or perquisites --install -v --dry-run')
def step_impl(context):
    context.code, context.response = context.execute(
        f"poetry run or perquisites --install -v --dry-run --no-telemetry"
    )
    assert context.code == 0


@then(u'install all missing tools')
def step_impl(context):
    assert "installing missing tools" in context.response
