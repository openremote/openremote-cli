# -*- coding: utf-8 -*-
# import logging
# import os
# from pathlib import Path
# import pkg_resources

from openremote_cli import shell


def deploy(password):
    shell.execute('docker volume create openremote_deployment-data')
    shell.execute(
        'docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:latest'
    )
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/swarm/swarm-docker-compose.yml'
    )
    shell.execute('docker swarm init')
    shell.execute(
        f'SETUP_ADMIN_PASSWORD={password} docker-compose -f swarm-docker-compose.yml -p openremote up -d'
    )


def remove():
    shell.execute(
        'wget -nc https://github.com/openremote/openremote/raw/master/swarm/swarm-docker-compose.yml'
    )
    shell.execute(
        f'docker-compose -f swarm-docker-compose.yml -p openremote down'
    )
