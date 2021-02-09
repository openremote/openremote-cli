from behave import *
#import sys
#from mock import patch
import subprocess


@given(u'we have docker and docker-compose installed')
def step_impl(context):
    subprocess.run(["docker", "-v"])
    subprocess.run(["docker-compose", "-v"])


@when(u'we call or-cli')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we call or-cli')


@then(u'show what will be done')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then show what will be done')


@then(u'deploy OpenRemote stack accordingly')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then deploy OpenRemote stack accordingly')
