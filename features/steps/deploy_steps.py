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
    assert 'aws cloudformation create-stack --stack-name ' in context.output


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
    assert '3.0.0' in context.output


@when(u'or deploy -a health --dnsname demo.openremote.io -vv')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy -a health --dnsname demo.openremote.io -vv --no-telemetry'
    )
    assert context.code == 0
    print(context.output)


@then(u'we get full health response')
def step_impl(context):
    assert 'version' in context.output


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


# Auto generate password
@when(u'or deploy --provider aws with default password')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy --provider aws -d test.aws.com -v -n -t'
    )
    assert context.code == 0
    print(context.output)


@then(u'generate password and email it to support')
def step_impl(context):
    assert 'Generated password:' in context.output
    assert (
        'An email with generated password would be sent to support@openremote.io'
        in context.output
    )


# Deploy localhost with custom dns name
@when(u'we call openremote-cli -n deploy --dnsname xxx.yyy.com')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy --dnsname xxx.yyy.com -v -t -n'
    )
    assert context.code == 0
    print(context.output)


@then(u'show what will be done with dns')
def step_impl(context):
    assert 'DOMAINNAME=xxx.yyy.com' in context.output
    assert 'PASSWORD=' in context.output
    assert (
        'docker-compose -f mvp-docker-compose.yml -p openremote up -d'
        in context.output
    )


@when(u'call or deploy --provider rich --dnsname rich -v -n -t')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run or deploy --provider rich --dnsname rich --password password -v -n -t'
    )
    assert context.code == 0
    print(context.output)


@then(u'fetch data from S3 (map is optional)')
def step_impl(context):
    assert (
        'aws s3 cp s3://openremote-mvp-map-storage/rich rich --storage-class STANDARD --recursive --profile openremote-cli --force-glacier-transfer'
        in context.output
    )
    assert 'tar xvf rich/deployment.tar.gz' in context.output


@then(u'deploy with on localhost with DNS rich.openremote.io')
def step_impl(context):
    assert (
        'PASSWORD=password DEPLOYMENT_NAME=rich docker-compose up -d'
        in context.output
    )


@when(u'or deploy --dnsname xxx.yyy.com --password xyz --dry-run -t')
def step_impl(context):
    context.code, context.output = context.execute(
        u'poetry run or deploy --dnsname xxx.yyy.com --password xyz --dry-run -t'
    )
    print(context.output)
    assert context.code == 0


@then(u'or sso --show --dnsname xxx.yyy.com -t contains password xyz')
def step_impl(context):
    context.code, context.output = context.execute(
        u'poetry run or sso --show --dnsname xxx.yyy.com -t'
    )
    print(context.output)
    assert '--password=xyz' in context.output
