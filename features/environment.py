from openremote_cli.shell import execute


def before_all(context):
    context.execute = execute
