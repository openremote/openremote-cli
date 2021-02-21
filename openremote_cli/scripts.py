# -*- coding: utf-8 -*-
import logging

# import os
# from pathlib import Path
# import pkg_resources

from openremote_cli import shell
from openremote_cli import config


def deploy(password):
    if config.DRY_RUN:
        print("dry-run active! Following commands would be executed:\n")
    shell.execute('docker volume create openremote_deployment-data')
    shell.execute('docker volume rm openremote_postgresql-data')
    shell.execute(
        'docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:latest'
    )
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/swarm/swarm-docker-compose.yml'
    )
    logging.getLogger().setLevel(logging.CRITICAL)  # surpress swarm init error
    shell.execute('docker swarm init')
    logging.getLogger().setLevel(config.LEVEL)
    if password != 'secret':
        shell.execute(
            f'SETUP_ADMIN_PASSWORD={password} docker stack deploy -c swarm-docker-compose.yml openremote'
        )
    else:
        shell.execute(
            f'docker stack deploy -c swarm-docker-compose.yml openremote'
        )


def remove():
    if config.DRY_RUN:
        print("--dry-run active! Following commands would be executed:\n")
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/swarm/swarm-docker-compose.yml'
    )
    shell.execute(f'docker stack rm openremote')
    shell.execute(f'rm -f swarm-docker-compose.yml')


def clean():
    if config.DRY_RUN:
        print("--dry-run active! Following commands would be executed:\n")
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/swarm/swarm-docker-compose.yml'
    )
    shell.execute(f'docker stack rm openremote')
    logging.error(
        'TODO: remove images. Now do it manually with docker rmi ...'
    )
    shell.execute(f'rm -f swarm-docker-compose.yml')
