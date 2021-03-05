# -*- coding: utf-8 -*-
from behave import *


@given(u'we have docker and docker-compose installed')
def step_impl(context):
    response_code, output = context.execute('docker -v')
    assert response_code == 0
    response_code, output = context.execute('docker-compose -v')
    assert response_code == 0


@when(u'we call openremote-cli --dry-run deploy --action create')
def step_impl(context):
    response_code, output = context.execute(
        f"poetry run openremote-cli --dry-run deploy --action create -n -vvv --no-telemetry"
    )
    print(output)
    context.response = output


@then(u'show what will be done')
def step_impl(context):
    assert (
        "docker volume create openremote_deployment-data" in context.response
    )
    assert (
        "docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:latest"
        in context.response
    )
    assert "docker stack deploy" in context.response


@when(u'we call or --dry-run deploy')
def step_impl(context):
    response_code, output = context.execute(
        f"poetry run openremote-cli deploy -n -vvv --no-telemetry"
    )
    context.response = output


@when(u'call openremote-cli deploy --action remove --dry-run')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy --action remove --dry-run -vvv --no-telemetry'
    )


@then(u'see that the stack is removed')
def step_impl(context):
    assert 'docker stack rm' in context.output


@when(u'call openremote-cli deploy --action clean --dry-run')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy --action clean --dry-run -v --no-telemetry'
    )


@then(u'remove volumes images and prune docker system')
def step_impl(context):
    print(context.output)
    assert 'docker volume rm' in context.output
    # assert 'docker rmi' in context.output # suppress errors
    assert 'docker system prune' in context.output


# Deploy to AWS
@when(u'call or deploy --provider aws -d -v --no-telemetry')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run or deploy --provider aws -n -v --no-telemetry'
    )
    print(context.output)
    assert context.code == 0


@then(u'download CloudFormation template from github')
def step_impl(context):
    # TODO check downloaded file
    pass


@then(u'execute AWS CloudFormation')
def step_impl(context):
    assert (
        'aws cloudformation create-stack --stack-name OpenRemote-'
        in context.output
    )


@when(u'call or deploy -a remove aws -d -v --no-telemetry')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy -a remove --provider aws -n -v --no-telemetry'
    )
    assert context.code == 0
    print(context.output)


@then(u'delete the proper cloudformation stack')
def step_impl(context):
    assert u'sh aws-delete-stack-' in context.output
    assert u'rm aws-delete-stack-' in context.output


# Healthcheck
import requests


@given(u'we have running openremote stack on a dnsname')
def step_impl(context):
    requests.get('https://demo.openremote.io')


@when(u'or deploy -a health --dnsname demo.openremote.io')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy -a health --dnsname demo.openremote.io --no-telemetry'
    )
    assert context.code == 0
    print(context.output)


@then(u'we get 0/1 health status')
def step_impl(context):
    assert '1.0' in context.output


@when(u'or deploy -a health --dnsname demo.openremote.io -v')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy -a health --dnsname demo.openremote.io -v --no-telemetry'
    )
    assert context.code == 0
    print(context.output)


@then(u'we get more info')
def step_impl(context):
    assert 'systemLoadPercentage' in context.output


@when(u'or deploy -a health --dnsname demo.openremote.io -vv')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy -a health --dnsname demo.openremote.io -vv --no-telemetry'
    )
    assert context.code == 0
    print(context.output)


@then(u'we get full health response')
def step_impl(context):
    assert 'processLoadPercentage' in context.output


# E-mail setup
@when(u'we call or deploy --with-email')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy --with-email -v -n --no-telemetry'
    )
    assert context.code == 0
    print(context.output)


@then(u'generate SMTP credentials')
def step_impl(context):
    assert 'aws iam create-user --user-name ses-user-' in context.output
    assert 'aws iam put-user-policy --policy-document' in context.output
    assert 'aws iam create-access-key --user-name ses-user-' in context.output
