from openremote_cli import config


@when(u'we login into demo.openremote.io with user and password')
def step_impl(context):
    context.code, context.output = context.execute(
        'poetry run openremote-cli manager --login -v -t'
    )
    assert context.code == 0
    print(context.output)


@then(u'we can list public assets from master realm')
def step_impl(context):
    # Check if we have some juice from it
    assert len(config.get_token('demo.openremote.io')) > 100
