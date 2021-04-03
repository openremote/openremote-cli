import os
import configparser
import logging

from pathlib import Path
from keycloak import KeycloakOpenID


def _config_file_name():
    return f'{str(Path.home())}/.openremote/config.ini'


# Declare it globally for this module to be robust against readonly runtime
config = configparser.ConfigParser()
config_file = True


def initialize():

    # user persistent config
    global TELEMETRY_URL, REGION, PROFILE, BUCKET, SMTP_SERVER

    config_file = True
    if not os.path.exists(_config_file_name()):
        try:
            os.makedirs(
                f'{str(Path.home())}/.openremote', mode=0o700, exist_ok=True
            )
        except:
            logging.error(f'Cannot create {str(Path.home())}/.openremote')
            config_file = False

    if config_file:
        config.read(_config_file_name())
    if config.sections() == []:
        try:
            try:
                config['DEFAULT'] = {
                    'telemetry_url': f"{os.environ['TELEMETRY_URL']}/metrics"
                }
            except:
                config['DEFAULT'] = {
                    'telemetry_url': 'https://cli.developers.openremote.io/metrics'
                }
            config['AWS'] = {
                'profile': 'openremote-cli',
                'bucket': 'openremote-mvp-map-storage',
                'region': 'eu-west-1',
            }
            with open(_config_file_name(), 'w') as conf:
                try:
                    config.write(conf)
                    print(f'Config created in {_config_file_name()}')
                except Exception as error:
                    logging.error(f'Error writing config: {conf}\n{error}')
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
    global DRY_RUN, LEVEL, VERBOSE, TELEMETRY, QUIET, TIMEOUT

    VERBOSE = False
    DRY_RUN = False
    TELEMETRY = True
    QUIET = False
    LEVEL = 'logging.ERROR'
    TIMEOUT = 20


def store_token(url, username, password, refresh):
    if config_file:
        config.read(_config_file_name())
    try:
        # first try to update
        managerUrl = config[url]
        managerUrl[f'{username}_password'] = password
        managerUrl['refresh_token'] = refresh
    except:
        # if not then create
        config[url] = {
            f'{username}_password': password,
            'refresh_token': refresh,
        }
    with open(_config_file_name(), 'w') as conf:
        try:
            config.write(conf)
        except Exception as error:
            logging.error(f'Error writing config: {conf}\n{error}')


def get_token(url):
    if config_file:
        config.read(_config_file_name())
    keycloak_openid = KeycloakOpenID(
        server_url=f'https://{url}/auth/',
        client_id="admin-cli",
        realm_name="master",
    )
    return keycloak_openid.refresh_token(config[url]['refresh_token'])[
        'access_token'
    ]


def get_password(url, username):
    if config_file:
        config.read(_config_file_name())
    password = 'secret'
    try:
        password = config[url][f'{username}_password']
    except:
        raise Exception(
            f'Password for {username} at {url} is unknown. Use:\nopenremote-cli manager --dnsname {url} --login -u {username} -p ...'
        )
    return password
