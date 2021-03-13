import os
import configparser
import logging

from pathlib import Path


def _config_file_name():
    return f'{str(Path.home())}/.openremote/config.ini'


def initialize():

    # user persistent config
    global TELEMETRY_URL, REGION, PROFILE, BUCKET, SMTP_SERVER

    config = configparser.ConfigParser()
    config.read(_config_file_name())

    if config.sections() == []:
        try:
            print('creating config file')
            if not os.path.exists(_config_file_name()):
                os.makedirs(
                    f'{str(Path.home())}/.openremote',
                    mode=0o700,
                    exist_ok=True,
                )
                config['DEFAULT'] = {
                    'telemetry_url': 'https://cli.developers.openremote.io/metrics'
                }
                config['AWS'] = {
                    'profile': 'openremote-cli',
                    'bucket': 'openremote-mvp-map-storage',
                    'region': 'eu-west-1',
                }
                with open(_config_file_name(), 'w') as conf:
                    config.write(conf)
        except Exception as error:
            logging.error(error)

    default = config['DEFAULT']
    TELEMETRY_URL = default['telemetry_url']
    try:
        if os.environ['TELEMETRY_URL']:
            TELEMETRY_URL = f"{os.environ['TELEMETRY_URL']}/metrics"
    except:
        pass

    # AWS parameters
    aws = config['AWS']
    PROFILE = aws['profile']
    BUCKET = aws['bucket']
    REGION = aws['region']
    SMTP_SERVER = f'email-smtp.{REGION}.amazonaws.com'

    # Runtime config
    global DRY_RUN, LEVEL, VERBOSE, TELEMETRY, QUIET

    VERBOSE = False
    DRY_RUN = False
    TELEMETRY = True
    QUIET = False
    LEVEL = 'logging.ERROR'

    store_token('localhost', 'secret_token')


def store_token(url, token):
    config = configparser.ConfigParser()
    config.read(_config_file_name())
    try:
        # first try to update
        managerUrl = config[url]
        managerUrl['token'] = token
    except:
        # if not the create
        config[url] = {'token': token}
    with open(_config_file_name(), 'w') as conf:
        config.write(conf)
