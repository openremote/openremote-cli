# -*- coding: utf-8 -*-
from behave import *

import subprocess
from openremote_cli.shell import execute


@given(u'we have docker and docker-compose installed')
def step_impl(context):
    response_code, output = execute('docker -v')
    assert response_code == 0
    response_code, output = execute('docker-compose -v')
    assert response_code == 0


@when(u'we call openremote-cli --dry-run deploy --action create')
def step_impl(context):
    response_code, output = execute(
        f"poetry run openremote-cli --dry-run deploy --action create"
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
    assert (
        "docker-compose -f swarm-docker-compose.yml -p openremote up -d"
        in context.response
    )


# @then(u'deploy OpenRemote stack accordingly')
# def step_impl(context):
#     raise NotImplementedError(
#         u'STEP: Then deploy OpenRemote stack accordingly'
#     )


@when(u'we call or --dry-run deploy')
def step_impl(context):
    response_code, output = execute(
        f"poetry run openremote-cli --dry-run deploy"
    )
    context.response = output
