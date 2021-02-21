# -*- coding: utf-8 -*-
from behave import *


@given(u'we have docker and docker-compose and wget installed')
def step_impl(context):
    response_code, output = context.execute('docker -v')
    assert response_code == 0
    response_code, output = context.execute('docker-compose -v')
    assert response_code == 0
    response_code, output = context.execute('wget -V')
    assert response_code == 0


@when(u'we call openremote-cli --dry-run deploy --action create')
def step_impl(context):
    response_code, output = context.execute(
        f"poetry run openremote-cli --dry-run deploy --action create -d"
    )
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
    assert (
        "wget -nc https://github.com/openremote/openremote/raw/master/swarm/swarm-docker-compose.yml"
        in context.response
    )
    assert "docker swarm init" in context.response
    assert "docker stack deploy" in context.response


@when(u'we call or --dry-run deploy')
def step_impl(context):
    response_code, output = context.execute(
        f"poetry run openremote-cli deploy -d -vvv"
    )
    context.response = output


@when(u'call openremote-cli deploy --action remove --dry-run')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy --action remove --dry-run'
    )


@then(u'see that the stack is removed')
def step_impl(context):
    assert 'docker stack rm' in context.output


@when(u'call openremote-cli deploy --action clean --dry-run')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli deploy --action clean --dry-run'
    )


@then(u'remove volumes images and prune docker system')
def step_impl(context):
    print(context.output)
    assert 'docker volume rm' in context.output
    assert 'docker rmi' in context.output
    assert 'docker system prune' in context.output
