from openremote_cli.shell import execute, config


def before_all(context):
    context.execute = execute
    config.initialize()


def before_feature(context, feature):
    if "skip" in feature.tags:
        feature.skip("Marked with @skip")
        return


def before_scenario(context, scenario):
    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")
        return
