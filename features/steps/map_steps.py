from behave import *


@given(u'we have aws installed')
def step_impl(context):
    response_code, output = context.execute('aws --version')
    assert response_code == 0


@when(
    u'we call openremote-cli map -a configure --id <id> --secret <secret> -d -v'
)
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli map -a configure --id id --secret secret -d -v --no-telemetry'
    )
    print(context.output)


@then(u'aws configure set profile.mvp-map-manager.aws_access_key_id <id>')
def step_impl(context):
    assert (
        'aws configure set profile.mvp-map-manager.aws_access_key_id id'
        in context.output
    )


@then(
    u'aws configure set profile.mvp-map-manager.aws_secret_access_key <secret>'
)
def step_impl(context):
    assert (
        'aws configure set profile.mvp-map-manager.aws_secret_access_key secret'
        in context.output
    )


@then(u'aws configure set profile.mvp-map-manager.region eu-west-1')
def step_impl(context):
    assert (
        'aws configure set profile.mvp-map-manager.region eu-west-1'
        in context.output
    )


@given(u'we have aws profile mvp-map-manager')
def step_impl(context):
    # TODO make it work in the pipeline on github
    # response_code, output = context.execute(
    #     'aws s3 ls --profile mvp-map-manager'
    # )
    # assert response_code == 0
    pass


@when(u'we call openremote-cli map -a upload -f file')
def step_impl(context):
    context.response_code, context.output = context.execute(
        u'poetry run openremote-cli map -a upload -f file --no-telemetry -v -d'
    )
    assert context.response_code == 0
    print(context.output)


@when(u'we call openremote-cli map -a list')
def step_impl(context):
    context.response_code, context.output = context.execute(
        'poetry run or map -a list --no-telemetry -v -d'
    )
    assert context.response_code == 0
    print(context.output)


@then(u'we see s3 ls command')
def step_impl(context):
    assert 'aws s3 ls' in context.output


@then(u'we see s3 cp command')
def step_impl(context):
    assert 'aws s3 cp' in context.output


@when(u'we call openremote-cli map -a download -f file')
def step_impl(context):
    context.response_code, context.output = context.execute(
        'poetry run or map -a download -f file --no-telemetry -v -d'
    )
    assert context.response_code == 0
    print(context.output)


@when(u'we call openremote-cli map -a delete -f file')
def step_impl(context):
    context.response_code, context.output = context.execute(
        u'poetry run or map -a delete -f file --no-telemetry -v -d'
    )
    assert context.response_code == 0
    print(context.output)


@then(u'we see s3 rm command')
def step_impl(context):
    assert 'aws s3 rm' in context.output
