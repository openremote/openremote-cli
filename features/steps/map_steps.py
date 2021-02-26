from behave import *


@given(u'we have aws profile openremote-cli')
def step_impl(context):
    # TODO make it work in the pipeline on github
    # response_code, output = context.execute(
    #     'aws s3 ls --profile openremote-cli'
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
