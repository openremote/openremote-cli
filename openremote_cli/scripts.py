# -*- coding: utf-8 -*-
import logging
import uuid

from openremote_cli import shell
from openremote_cli import config


def deploy(password):
    logging.getLogger().setLevel(logging.CRITICAL)  # surpress some errors
    shell.execute('docker swarm init')
    shell.execute('docker volume rm openremote_postgresql-data')
    logging.getLogger().setLevel(config.LEVEL)
    shell.execute('docker volume create openremote_deployment-data')
    shell.execute(
        'docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:latest'
    )
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/mvp/swarm-docker-compose.yml'
    )
    if password != 'secret':
        shell.execute(
            f'SETUP_ADMIN_PASSWORD={password} docker stack deploy -c swarm-docker-compose.yml openremote'
        )
    else:
        shell.execute(
            f'docker stack deploy -c swarm-docker-compose.yml openremote'
        )
    shell.execute(f'rm -f swarm-docker-compose.yml')
    if config.VERBOSE is True:
        print(
            '\nCheck running services with `docker service ls` until all are 1/1 replicas...'
        )
        print('then open http://localhost')


def deploy_aws(password, url='demo.mvp.openremote.io'):
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/mvp/aws-cloudformation.template.yml'
    )
    shell.execute(
        f'aws cloudformation create-stack --stack-name OpenRemote-{uuid.uuid4()} '
        f'--template-body file://aws-cloudformation.template.yml --parameters '
        f'ParameterKey=DomainName,ParameterValue=mvp.openremote.io '
        f'ParameterKey=HostName,ParameterValue=demo '
        f'ParameterKey=HostedZone,ParameterValue=true '
        f'ParameterKey=OpenRemotePassword,ParameterValue={password} '
        f'ParameterKey=InstanceType,ParameterValue=t3a.small '
        f'ParameterKey=KeyName,ParameterValue=openremote --profile={config.PROFILE}'
    )
    shell.execute(f'rm -f aws-cloudformation.template.yml')


def remove():
    shell.execute(f'docker stack rm openremote')


def clean():
    shell.execute(
        'docker volume rm --force openremote_deployment-data openremote_postgresql-data openremote_proxy-data'
    )
    logging.getLogger().setLevel(logging.CRITICAL)  # surpress some errors
    shell.execute(
        'docker rmi openremote/manager-swarm openremote/deployment '
        'openremote/keycloak openremote/postgresql openremote/proxy '
    )
    logging.getLogger().setLevel(config.LEVEL)
    shell.execute('docker system prune --force')


def configure_aws(id, secret, region):
    print(
        shell.execute(
            f'aws configure set profile.{config.PROFILE}.aws_access_key_id {id}'
        )[1]
    )
    print(
        shell.execute(
            f'aws configure set profile.{config.PROFILE}.aws_secret_access_key {secret}'
        )[1]
    )
    print(
        shell.execute(
            f'aws configure set profile.{config.PROFILE}.region {region}'
        )[1]
    )


def map_upload(path):
    print(
        shell.execute(
            f'aws s3 cp {path} s3://{config.BUCKET} --profile {config.PROFILE}'
        )[1]
    )


def map_list():
    print(
        shell.execute(
            f'aws s3 ls s3://{config.BUCKET} --profile {config.PROFILE}'
        )[1]
    )


def map_download(path):
    print(
        shell.execute(
            f'aws s3 cp s3://{config.BUCKET}/{path} {path} --profile {config.PROFILE}'
        )[1]
    )


def map_delete(path):
    print(
        shell.execute(
            f'aws s3 rm s3://{config.BUCKET}/{path} --profile  {config.PROFILE}'
        )[1]
    )
