import os


def initialize():
    global DRY_RUN, LEVEL, TELEMETRY_URL
    DRY_RUN = False
    LEVEL = 'logging.ERROR'
    try:
        TELEMETRY_URL = f"{os.environ['TELEMETRY_URL']}/metrics"
    except:
        TELEMETRY_URL = 'http://localhost:8080/metrics'
