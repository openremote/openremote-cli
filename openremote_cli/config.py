import os


def initialize():
    global DRY_RUN, LEVEL, SMTP_SERVER, TELEMETRY_URL, VERBOSE, PROFILE, BUCKET, TELEMETRY, REGION, QUIET

    # AWS parameters
    PROFILE = 'openremote-cli'
    BUCKET = 'openremote-mvp-map-storage'
    REGION = 'eu-west-1'
    SMTP_SERVER = f'email-smtp.{REGION}.amazonaws.com'

    VERBOSE = False
    DRY_RUN = False
    TELEMETRY = True
    QUIET = False
    LEVEL = 'logging.ERROR'
    TELEMETRY_URL = 'https://cli.developers.openremote.io/metrics'
    try:
        if os.environ['TELEMETRY_URL']:
            TELEMETRY_URL = f"{os.environ['TELEMETRY_URL']}/metrics"
    except:
        pass
