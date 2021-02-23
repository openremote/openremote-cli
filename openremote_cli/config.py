import os


def initialize():
    global DRY_RUN, LEVEL, TELEMETRY_URL, VERBOSE
    VERBOSE = False
    DRY_RUN = False
    LEVEL = 'logging.ERROR'
    TELEMETRY_URL = 'https://cli.developers.openremote.io/metrics'
    try:
        if os.environ['TELEMETRY_URL']:
            TELEMETRY_URL = f"{os.environ['TELEMETRY_URL']}/metrics"
    except:
        pass
