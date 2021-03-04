# -*- coding: utf-8 -*-
import logging
import uuid
import wget
import json
import urllib.request
import os

from openremote_cli import shell
from openremote_cli import config


def deploy(password):
    shell.execute('docker swarm init', no_exception=True)
    shell.execute(
        'docker volume rm openremote_postgresql-data', no_exception=True
    )
    shell.execute('docker volume create openremote_deployment-data')
    shell.execute(
        'docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:latest'
    )
    if not config.DRY_RUN:
        wget.download(
            'https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
        )
    if config.VERBOSE is True:
        print(
            '> wget -nc https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
        )
    if password != 'secret':
        shell.execute(
            f'SETUP_ADMIN_PASSWORD={password} docker stack deploy -c mvp-docker-compose.yml openremote'
        )
    else:
        shell.execute(
            f'docker stack deploy -c mvp-docker-compose.yml openremote'
        )
    if not config.DRY_RUN:
        os.remove(f'mvp-docker-compose.yml')
    if config.VERBOSE is True:
        print(
            '\nCheck running services with `docker service ls` until all are 1/1 replicas...'
        )
        print('then open http://localhost')


def deploy_health(dnsname, verbosity=0):
    try:
        health = json.loads(
            urllib.request.urlopen(
                f'https://{dnsname}/api/master/health'
            ).read()
        )
        if verbosity == 0:
            print(health['system']['version'])
        elif verbosity == 1:
            print(health['system'])
        else:
            print(health)
    except:
        if verbosity == 0:
            print('0')
        else:
            print(f'Error calling\ncurl https://{dnsname}/api/master/health')


def deploy_aws(password, dnsname):
    host = dnsname.split('.')[0]
    domain = dnsname[len(host) + 1 :]
    stack_name = f'OpenRemote-{uuid.uuid4()}'
    check_aws_perquisites()
    if not config.DRY_RUN:
        wget.download(
            'https://github.com/openremote/openremote/raw/master/mvp/aws-cloudformation.template.yml'
        )
    if config.VERBOSE is True:
        print(
            '> wget -nc https://github.com/openremote/openremote/raw/master/mvp/aws-cloudformation.template.yml'
        )

    shell_exec = shell.execute(
        f'aws cloudformation create-stack --stack-name {stack_name} '
        f'--template-body file://aws-cloudformation.template.yml --parameters '
        f'ParameterKey=DomainName,ParameterValue={domain} '
        f'ParameterKey=HostName,ParameterValue={host} '
        f'ParameterKey=HostedZone,ParameterValue=true '
        f'ParameterKey=OpenRemotePassword,ParameterValue={password} '
        f'ParameterKey=InstanceType,ParameterValue=t3a.small '
        f'ParameterKey=KeyName,ParameterValue=openremote --profile={config.PROFILE}'
    )
    print(f'\n{shell_exec[1]}')
    if shell_exec[0] != 0:
        raise Exception(shell_exec)

    print('Waiting for CloudFormation...')
    shell.execute(
        f'aws cloudformation wait stack-create-complete '
        f'--stack-name {stack_name} --profile {config.PROFILE}'
    )

    if not config.DRY_RUN:
        os.remove(f'aws-cloudformation.template.yml')
    shell.execute(
        f'echo "aws cloudformation delete-stack --stack-name {stack_name} --profile {config.PROFILE}" > aws-delete-stack-{dnsname}.sh'
    )
    shell.execute(f'chmod +x aws-delete-stack-{dnsname}.sh')
    print(
        f'\nStack deployed. Mind that running it cost money! To free resources execute:\n'
        f'aws cloudformation delete-stack --stack-name {stack_name} --profile {config.PROFILE}\n\n'
        f'check running stack with health command:\n'
        f'or deploy -a health --dnsname {dnsname} -v'
    )


def remove_aws(dnsname):
    check_aws_perquisites()
    shell.execute(f'sh aws-delete-stack-{dnsname}.sh')
    if config.VERBOSE:
        print(f'rm aws-delete-stack-{dnsname}.sh')
    if not config.DRY_RUN:
        os.remove(f'aws-delete-stack-{dnsname}.sh')


def remove():
    shell.execute(f'docker stack rm openremote')


def clean():
    shell.execute(
        'docker volume rm --force openremote_deployment-data openremote_postgresql-data openremote_proxy-data'
    )
    shell.execute(
        'docker rmi openremote/manager-swarm openremote/deployment '
        'openremote/keycloak openremote/postgresql openremote/proxy ',
        no_exception=True,
    )
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


def check_tools():
    print('Checking AWS perquisites')
    return check_aws_perquisites()


def check_aws_perquisites():
    # Check AWS profile
    code, output = shell.execute('aws configure list-profiles')
    if not config.DRY_RUN and 'openremote-cli' not in output:
        msg = "aws-cli profile 'openremote-cli' missing"
        logging.error(msg)
        raise Exception(1, msg)
    # Check EC2 key
    code, output = shell.execute(
        'aws ec2 describe-key-pairs --key-names openremote'
    )
    if not config.DRY_RUN and 'openremote' not in output:
        msg = "ERROR: Missing EC2 keypair 'openremote' in eu-west-1 region (Ireland)"
        logging.error(msg)
        raise Exception("Missing EC2 keypair 'openremote' in eu-west-1")
    return True
