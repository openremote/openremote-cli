from openremote_cli.shell import execute, config


def before_all(context):
    context.execute = execute
    config.initialize()
