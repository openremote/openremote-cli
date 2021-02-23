# -*- coding: utf-8 -*-
import logging

# import os
# from pathlib import Path
# import pkg_resources

from openremote_cli import shell
from openremote_cli import config


def deploy(password):
    if config.DRY_RUN:
        print("dry-run active!\n")
    if not config.VERBOSE:
        print("To see commands use -v switch\n")
    logging.getLogger().setLevel(logging.CRITICAL)  # surpress some errors
    shell.execute('docker swarm init')
    shell.execute('docker volume rm openremote_postgresql-data')
    logging.getLogger().setLevel(config.LEVEL)
    shell.execute('docker volume create openremote_deployment-data')
    shell.execute(
        'docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:latest'
    )
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/swarm/swarm-docker-compose.yml'
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


def remove():
    if config.DRY_RUN:
        print("--dry-run active!")
    shell.execute(f'docker stack rm openremote')


def clean():
    if config.DRY_RUN:
        print("--dry-run active!")
    shell.execute(
        'docker volume rm --force openremote_deployment-data openremote_postgresql-data openremote_proxy-data'
    )
    logging.getLogger().setLevel(logging.CRITICAL)  # surpress some errors
    shell.execute(
        'docker rmi openremote/manager-swarm openremote/deployment openremote/keycloak openremote/postgresql openremote/proxy '
    )
    logging.getLogger().setLevel(config.LEVEL)
    shell.execute('docker system prune --force')
