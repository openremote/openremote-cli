# -*- coding: utf-8 -*-
import logging
import uuid
import wget
import json
import urllib.request
import os
import string
import requests
import ssl
import time
import emojis
import re
import functools
import argparse
import sys


from keycloak import KeycloakOpenID
from random import choice, randint
from openremote_cli import shell
from openremote_cli import config
from openremote_cli import gen_aws_smtp_credentials, email
from webbot import Browser
from selenium.common.exceptions import WebDriverException


def deploy(password, smtp_user, smtp_password, dnsname):
    shell.execute('docker swarm init', no_exception=True)
    shell.execute(
        'docker volume rm openremote_postgresql-data', no_exception=True
    )
    # TODO fetch tar from S3 and copy to the docker volume
    # shell.execute('docker volume create openremote_deployment-data')
    # shell.execute(
    #     'docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:mvp'
    # )
    if config.VERBOSE is True:
        print(
            '> wget -nc https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
        )
    if not config.DRY_RUN:
        wget.download(
            'https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
        )
    env = ''
    if password != 'secret':
        env = f'PASSWORD={password} '
    if smtp_user and smtp_password:
        env = (
            f'{env}EMAIL_USER={smtp_user} '
            f'EMAIL_PASSWORD={smtp_password} '
            f'EMAIL_HOST=email-smtp.{config.REGION}.amazonaws.com '
        )
    if dnsname != 'localhost':
        identity = dnsname
        if _check_ip(dnsname):  # it is pure IP
            dnsname = 'localhost'  # prevent proxy from issuing cert
        env = f'{env}DOMAINNAME={dnsname} IDENTITY_NETWORK_HOST={identity} '
        # As you may be facing internet change default password for security
        generate_password, password = _password(password)
        if generate_password:
            env = f'{env}PASSWORD={password} '
        # Deploy with docker-compose as proxy container does not obey
        # health check within swarm mode
        # TODO revisit proxy image to fix this, otherwise letsencrypt has problems
        shell.execute(
            f'{env}docker-compose -f mvp-docker-compose.yml -p openremote up -d'
        )
        if not config.DRY_RUN:
            print('\nStack deployed, waiting for startup to complete', end=' ')
            while _deploy_health(dnsname, 0) == 0:
                time.sleep(3)
                print('.', end='', flush=True)
            print(emojis.encode(':thumbsup:\n'))
        if config.VERBOSE is True:
            print(
                f'Open https://{dnsname} and login with admin:{password}\n\n'
                'Remove the stack when you are done:\n'
                '> docker-compose -f mvp-docker-compose.yml -p openremote down\n'
                '> rm mvp-docker-compose.yml\n'
            )
    else:
        shell.execute(
            f'{env}docker stack deploy -c mvp-docker-compose.yml openremote'
        )
        if not config.DRY_RUN:
            print('\nStack deployed, waiting for startup to complete', end=' ')
            c = 0
            # TODO deploying from docker image has problems with health checking hence 10min time out
            while _deploy_health(dnsname, 0) == 0 and c < 200:
                time.sleep(3)
                print('.', end='', flush=True)
                c += 1
            print(emojis.encode(':thumbsup:\n'))
        if config.VERBOSE is True:
            print(
                f'\nOpen https://localhost and login with admin:{password}\n\n'
                'To remove the stack when you are done:\n'
                '> docker stack rm openremote\n'
            )
        if not config.DRY_RUN:
            os.remove(f'mvp-docker-compose.yml')
    if config.VERBOSE is True:
        print(
            'To remove docker resources:\n'
            "> docker images --filter 'reference=openremote/*' -q | xargs docker rmi\n"
            "> docker volume ls --filter 'dangling=true' -q | xargs docker volume rm"
        )


def deploy_health(dnsname, verbosity=0):
    print(_deploy_health(dnsname, verbosity))


def _deploy_health(dnsname, verbosity):
    try:
        # We need this for self-signed certs like localhost
        ssl._create_default_https_context = ssl._create_unverified_context
        health = json.loads(
            urllib.request.urlopen(
                f'https://{dnsname}/api/master/health'
            ).read()
        )
        if verbosity == 0:
            return health['system']['version']
        elif verbosity == 1:
            return health['system']
        else:
            return health
    except:
        if '.' not in dnsname and dnsname != 'localhost':
            host, domain = _split_dns(dnsname)
            deploy_health(f'{host}.{domain}', verbosity)
        elif verbosity == 0:
            return 0
        else:
            return f'Error calling\ncurl https://{dnsname}/api/master/health'


def _split_dns(dnsname):
    if '.' in dnsname:
        host = dnsname.split('.')[0]
        domain = dnsname[len(host) + 1 :]
    else:
        logging.debug('adding default domain')
        host = dnsname
        domain = 'mvp.openremote.io'
    return host, domain


def _password(password):
    generate_password = password == 'secret'
    if generate_password:
        characters = string.ascii_letters + string.digits
        password = "".join(choice(characters) for x in range(randint(8, 16)))
        if not config.QUIET:
            print(f'\nGenerated password: {password}\n')
    return generate_password, password


def deploy_aws(password, dnsname):
    host, domain = _split_dns(dnsname)
    logging.debug(f'{dnsname} => {host} + {domain}')
    stack_name = f'{host}-{uuid.uuid4()}'
    check_aws_perquisites()
    generate_password, password = _password(password)
    if config.VERBOSE is True:
        print(
            '> wget -nc https://github.com/openremote/openremote/raw/master/mvp/aws-cloudformation.template.yml'
        )
    if not config.DRY_RUN:
        wget.download(
            'https://github.com/openremote/openremote/raw/master/mvp/aws-cloudformation.template.yml'
        )
    shell_exec = shell.execute(
        f'aws cloudformation create-stack --stack-name {stack_name} '
        f'--template-body file://aws-cloudformation.template.yml --parameters '
        f'ParameterKey=DomainName,ParameterValue={domain} '
        f'ParameterKey=HostName,ParameterValue={host} '
        f'ParameterKey=HostedZone,ParameterValue=true '
        f'ParameterKey=OpenRemotePassword,ParameterValue={password} '
        f'ParameterKey=InstanceType,ParameterValue=t3a.small '
        f'ParameterKey=KeyName,ParameterValue=openremote '
        f'--capabilities CAPABILITY_NAMED_IAM '
        f'--profile={config.PROFILE}'
    )
    print(f'\n{shell_exec[1]}')
    if shell_exec[0] != 0:
        raise Exception(shell_exec)

    print('Waiting for CloudFormation...')
    # TODO make better feedback to the user
    # code, output = shell.execute
    # CREATE_STACK_STATUS=$(aws --region ${AWS_REGION} --profile ${AWS_PROFILE} cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].StackStatus' --output text)
    # while [[ $CREATE_STACK_STATUS == "REVIEW_IN_PROGRESS" ]] || [[ $CREATE_STACK_STATUS == "CREATE_IN_PROGRESS" ]]
    # do
    #     # Wait 30 seconds and then check stack status again
    #     sleep 30
    #     CREATE_STACK_STATUS=$(aws --region ${AWS_REGION} --profile ${AWS_PROFILE} cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].StackStatus' --output text)
    # done
    shell.execute(
        f'aws cloudformation wait stack-create-complete '
        f'--stack-name {stack_name} --profile {config.PROFILE}'
    )
    if not config.DRY_RUN:
        os.remove(f'aws-cloudformation.template.yml')
        if generate_password:
            # In case of password generation get email credentials and send it to support
            code, output = shell.execute(
                f'aws cloudformation describe-stacks --stack-name {stack_name} --profile {config.PROFILE} '
                '--query "Stacks[0].Outputs[?OutputKey==\'UserId\'||OutputKey==\'UserSecret\'].OutputValue" --output json'
            )
            credentials = json.loads(output)
            smtp_user = credentials[0]
            smtp_password = gen_aws_smtp_credentials.calculate_key(
                credentials[1], config.REGION
            )
            email.sendmail(
                "michal.rutka@gmail.com",
                "Openremote password",
                f"""
                A new AWS stack {stack_name} has been just created. Because there was a
                default password used a more secure one was generated. The new admin password is
                {password}
                """,
                smtp_user,
                smtp_password,
            )
            print(
                '\nAn email with generated password was sent to support@openremote.io\n'
            )
    elif generate_password:
        print(
            '\nAn email with generated password would be sent to support@openremote.io\n'
        )
    if not config.DRY_RUN:
        if os.name == "nt":
            shell.execute(
                f'echo "aws cloudformation delete-stack --stack-name {stack_name} --profile {config.PROFILE}" > aws-delete-stack-{host}.{domain}.bat'
            )
        else:
            shell.execute(
                f'echo "aws cloudformation delete-stack --stack-name {stack_name} --profile {config.PROFILE}" > aws-delete-stack-{host}.{domain}.sh'
            )
            shell.execute(f'chmod +x aws-delete-stack-{host}.{domain}.sh')
        print('\nStack deployed, waiting for startup to complete', end=' ')
        c = 0
        while _deploy_health(f'{host}.{domain}', 0) == 0 and c < 200:
            time.sleep(3)
            print('.', end='', flush=True)
            c += 1
        print(emojis.encode(':thumbsup:\n'))
    print(
        emojis.encode(
            '\nMind that running it cost money :moneybag::moneybag::moneybag:! To free resources execute:\n\n'
            f'aws cloudformation delete-stack --stack-name {stack_name} --profile {config.PROFILE}\n\n'
            'check running stack with health command:\n'
            f'or deploy -a health --dnsname {host}.{domain} -v'
        )
    )


def remove_aws(dnsname):
    check_aws_perquisites()
    if os.name == "nt":
        if config.VERBOSE:
            print(f'del aws-delete-stack-{dnsname}.bat')
        shell.execute(f'aws-delete-stack-{dnsname}.bat')
        if not config.DRY_RUN:
            os.remove(f'aws-delete-stack-{dnsname}.bat')
    else:
        if config.VERBOSE:
            print(f'rm aws-delete-stack-{dnsname}.sh')
        shell.execute(f'sh aws-delete-stack-{dnsname}.sh')
        if not config.DRY_RUN:
            os.remove(f'aws-delete-stack-{dnsname}.sh')


def remove(dnsname):
    if dnsname == 'localhost':
        shell.execute(f'docker stack rm openremote')
    else:
        if config.VERBOSE is True:
            print(
                '> wget -nc https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
            )
        if not config.DRY_RUN:
            wget.download(
                'https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
            )
        shell.execute(
            f'docker-compose -f mvp-docker-compose.yml -p openremote down'
        )


def clean():
    shell.execute(
        'docker volume rm --force openremote_deployment-data openremote_postgresql-data openremote_proxy-data'
    )
    shell.execute(
        'docker rmi openremote/manager-swarm openremote/deployment '
        'openremote/keycloak openremote/postgresql openremote/proxy '
        'openremote/manager',
        no_exception=True,
    )
    shell.execute('docker system prune --force')


def configure_aws(id, secret, region):
    config.REGION = region
    shell.execute(
        f'aws configure set profile.{config.PROFILE}.aws_access_key_id {id}',
        echo=config.VERBOSE,
    )
    shell.execute(
        f'aws configure set profile.{config.PROFILE}.aws_secret_access_key {secret}',
        echo=config.VERBOSE,
    )
    shell.execute(
        f'aws configure set profile.{config.PROFILE}.region {region}',
        echo=config.VERBOSE,
    )


def configure_aws_show():
    if not config.QUIET:
        print(f'S3 bucket: s3://{config.BUCKET}\n')
        region = shell.execute(
            f'aws configure get region --profile {config.PROFILE}'
        )[1][:-1]
        id = shell.execute(
            f'aws configure get aws_access_key_id --profile {config.PROFILE}'
        )[1][:-1]
        secret = shell.execute(
            f'aws configure get aws_secret_access_key --profile {config.PROFILE}'
        )[1][:-1]
        print(f'--id={id} --secret="{secret}" --region={region}')


def map_upload(path):
    shell.execute(
        f'aws s3 cp {path} s3://{config.BUCKET}/{path} --profile {config.PROFILE}',
        echo=True,
    )
    shell.execute(
        'aws s3api put-object-tagging --bucket %s --key %s --tagging \'TagSet=[{Key=type,Value=deployment-data}]\' --profile %s'
        % (config.BUCKET, path, config.PROFILE),
        echo=True,
    )


def map_list(path):
    shell.execute(
        f'aws s3 ls s3://{config.BUCKET}/{path} --recursive --human-readable --summarize --profile {config.PROFILE}',
        echo=True,
    )


def map_download(path):
    shell.execute(
        f'aws s3 cp s3://{config.BUCKET}/{path} {path} --recursive --profile {config.PROFILE}',
        echo=True,
    )


def map_delete(path):
    shell.execute(
        # No --recursive here as it can wipe the whole bucket, also for other clients
        f'aws s3 rm s3://{config.BUCKET}/{path} --profile {config.PROFILE}',
        echo=True,
    )


def check_tools():
    def _show_check_result(tool):
        code, output = shell.execute(tool, no_exception=True)
        if not config.QUIET:
            print(f'{output.rstrip()} ', end='')
            print(emojis.encode(':heavy_check_mark:')) if code == 0 else print(
                emojis.encode(':x:')
            )
        elif code != 0:
            raise Exception(f'{code}, {output}')

    _show_check_result('docker --version')
    _show_check_result('docker-compose --version')
    _show_check_result('aws --version')
    return check_aws_perquisites()


def check_aws_perquisites():
    # Check AWS profile
    code, output = shell.execute('aws configure list-profiles')
    if not config.DRY_RUN and config.PROFILE not in output:
        msg = f"aws-cli profile '{config.PROFILE}' missing"
        raise Exception(-1, msg)
    # Check EC2 key
    code, output = shell.execute(
        f'aws ec2 describe-key-pairs --key-names openremote --profile {config.PROFILE}'
    )
    if not config.DRY_RUN and 'openremote' not in output:
        msg = f"ERROR: Missing EC2 keypair 'openremote' in {config.REGION} region (Ireland)"
        raise Exception(-1, msg)
    return True


# E-mail credentials
def smtp_credentials(dnsname):
    if dnsname == 'localhost':
        user_name = f'ses-user-{dnsname}-{uuid.uuid4()}'
    else:
        user_name = f'ses-user-{dnsname}'
    code, output = shell.execute(
        f'aws iam create-user --user-name {user_name} --profile {config.PROFILE} --output json'
    )
    logging.debug(output)
    code, output = shell.execute(
        'aws iam put-user-policy --policy-document \'{"Version": "2012-10-17",'
        '"Statement":[{"Effect": "Allow","Action": "ses:SendRawEmail","Resource": "*"}]}\''
        f' --policy-name OpenRemoteSendEmail --user-name {user_name} --profile {config.PROFILE}'
    )
    code, output = shell.execute(
        f'aws iam create-access-key --user-name {user_name} --profile {config.PROFILE} --output json'
    )
    if config.DRY_RUN:
        return 'AccessKeyId', 'SecretAccessKey'
    else:
        logging.debug(output)
        access = json.loads(output)
        return (
            access['AccessKey']['AccessKeyId'],
            gen_aws_smtp_credentials.calculate_key(
                access['AccessKey']['SecretAccessKey'], config.REGION
            ),
        )


# Manager
def manager_login(url, username, password):
    realm = 'master'
    if username == 'smartcity':
        realm = 'smartcity'
    keycloak_openid = KeycloakOpenID(
        server_url=f'https://{url}/auth/',
        client_id="admin-cli",
        realm_name=realm,
        client_secret_key="secret",
    )
    if password:
        response = keycloak_openid.token(username, password)
    else:
        password = config.get_password(url, username)
        response = keycloak_openid.token(username, password)
    config.store_token(url, username, password, response['refresh_token'])


def manager_list_realms(dnsname):
    response = requests.get(
        f'https://{dnsname}/auth/admin/realms',
        headers={'Authorization': f'Bearer ' + config.get_token(dnsname)},
    )
    for r in response.json():
        if config.QUIET:
            print(f"{r['realm']}  \t{r['displayName']}")
        else:
            print(json.dumps(r, indent=2))


def manager_list_users(realm, dnsname):
    response = requests.get(
        f'https://{dnsname}/auth/admin/realms/{realm}/users',
        headers=_bearer(dnsname),
    )
    for r in response.json():
        if config.QUIET:
            print(f"{r['firstName']} {r['lastName']}\t-\t{r['username']}")
        else:
            print(json.dumps(r, indent=2))


def manager_list_public_assets(realm, dnsname):
    response = requests.post(
        f'https://{dnsname}/api/{realm}/asset/public/query',
        # headers=_bearer(dnsname), # TODO why it gives 401 with smartcity realm and not with master?
        json={
            "select": {"include": "ALL_EXCEPT_PATH"},
            "type": {
                "predicateType": "string",
                "value": "urn:openremote:asset:thing",
            },
        },
    )
    for r in response.json():
        if config.QUIET:
            print(f"{r['type']}\t{r['name']}")
        else:
            print(json.dumps(r, indent=2))


def _bearer(dnsname):
    return {'Authorization': f'Bearer ' + config.get_token(dnsname)}


def _check_ip(ip):
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    return re.search(regex, ip)


# Richard's way
def deploy_rich(password, smtp_user, smtp_password, project):
    staging = False
    if project.find('staging.') == 0:
        staging = True
        project = project[8:]
    shell.execute(
        f'aws s3 cp s3://{config.BUCKET}/{project} {project} --recursive --profile {config.PROFILE}'
    )
    shell.execute(f'tar xvf {project}/deployment.tar.gz')
    shell.execute(f'mv mapdata.mbtiles deployment/map/', no_exception=True)
    env = ''
    # TODO reuse installed credentials docker run {project_manager_1} env
    if password != 'secret':
        env = f'PASSWORD={password} '
    if smtp_user and smtp_password:
        env = (
            f'{env}EMAIL_USER={smtp_user} '
            f'EMAIL_PASSWORD={smtp_password} '
            f'EMAIL_HOST=email-smtp.{config.REGION}.amazonaws.com '
        )
    dnsname = f'{project}.openremote.io'
    if staging:
        env = f'{env}DEPLOYMENT_NAME=staging.{project} '
    else:
        env = f'{env}DEPLOYMENT_NAME={project} '
    generate_password, password = _password(password)
    if generate_password:
        env = f'{env}PASSWORD={password} '
    shell.execute(f'{env}docker-compose up -d')
    if not config.DRY_RUN:
        print('\nStack deployed, waiting for startup to complete', end=' ')
        while _deploy_health(dnsname, 0) == 0:
            time.sleep(3)
            print('.', end='', flush=True)
        print(emojis.encode(':thumbsup:'))
    if config.VERBOSE is True:
        print(f'\nOpen https://{dnsname} and login with admin:{password}')


def manager_open(url, user, quit, realm='master'):
    driver = _manager_ui_login(url, user, realm=realm)
    _manager_ui_wait_map(driver, url)
    if quit:
        # Need this for manager to act (maybe some confirmation TODO)
        time.sleep(1)
    else:
        input('Press ENTER to quit')


def _manager_ui_login(url, user, realm, delay=30):
    if config.DRY_RUN:
        return Browser(showWindow=False)
    browser_options = (
        ['ignore-certificate-errors'] if url == 'localhost' else []
    )
    driver = Browser(
        showWindow=not config.QUIET, browser_options=browser_options
    )
    start = time.time()
    end = start
    driver.go_to(f'https://{url}/manager/?realm={realm}')
    while not driver.exists('LOG IN') and not driver.exists('SIGN IN'):
        if not config.QUIET:
            print('+', end='', flush=True)
        time.sleep(0.2)
        end = time.time()
        if end - start > delay:
            raise Exception(f'{url}: no login page after {delay}s')
    driver.type(user, into='username')
    driver.type(config.get_password(url, user), into='password')
    driver.click('SIGN IN')
    driver.click('LOG IN')
    end = time.time()
    print(f'{url} login time\t{end-start:.2f}s')
    return driver


def timeout(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if config.DRY_RUN:
            return 0
        start = time.time()
        while time.time() - start < config.TIMEOUT:
            try:
                result = func(*args, **kwargs)
                print(f' {func.__name__!r}: OK {time.time() - start:.2f}s')
                return result
            except WebDriverException:
                if not config.QUIET:
                    print('.', end='', flush=True)
                time.sleep(0.1)
            except Exception as e:
                logging.error(f'Exception {e.__class__} in {func.__name__}')
        if config.QUIET:
            raise Exception(f'{func.__name__!r}: timeout {config.TIMEOUT}s')
        else:
            logging.error(f'{func.__name__!r}: timeout {config.TIMEOUT}s')
        return -1

    return inner


@timeout
def _manager_ui_wait_map(driver, url):
    driver.execute_script(
        "document.querySelector('or-app').shadowRoot"
        ".querySelector('page-map').shadowRoot"
    )


@timeout
def _manager_ui_add_asset_dialog(driver, url):
    driver.execute_script(
        "document.querySelector('or-app').shadowRoot"
        ".querySelector('page-assets').shadowRoot"
        ".querySelector('or-asset-tree').shadowRoot"
        ".querySelector('or-mwc-input[icon=plus]').shadowRoot"
        ".querySelector('button').click()"
    )


@timeout
def _manager_ui_add_http_weather_agent(driver, url):
    driver.execute_script(
        "document.querySelector('or-mwc-dialog').shadowRoot"
        ".querySelector('or-add-asset-dialog').shadowRoot"
        ".querySelector('or-mwc-input').shadowRoot"
        ".querySelector('input').value = 'Weather Agent'"
    )
    driver.execute_script(
        "document.querySelector('or-mwc-dialog').shadowRoot"
        ".querySelector('or-add-asset-dialog').shadowRoot"
        ".querySelector('or-mwc-input').shadowRoot.querySelector('input')"
        ".dispatchEvent(new Event('change'))"
    )


@timeout
def _manager_ui_select_http_agent(driver, url):
    driver.execute_script(
        "document.querySelector('or-mwc-dialog').shadowRoot.querySelector('or-add-asset-dialog').shadowRoot.querySelector('or-mwc-list').shadowRoot.querySelectorAll('span')[3].click()"
    )


@timeout
def _manager_ui_press_add(driver, url):
    driver.execute_script(
        "document.querySelector('or-mwc-dialog').shadowRoot.querySelector('or-mwc-input[id=add-btn]').click()"
    )


# Tests in parallel example https://github.com/varungv/MultiThreadingSample


def manager_test_http_rest(delay=1, quit=True):
    if not hasattr(config, 'DRY_RUN'):
        # When running directly from installed scripts
        config.initialize()
        parser = argparse.ArgumentParser(
            description=f'Test plan HTTP REST',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            '-u',
            '--user',
            type=str,
            required=False,
            help='username',
            default='admin',
        )
        parser.add_argument(
            '-p', '--password', required=False, help='user password'
        )
        parser.add_argument(
            '-d',
            '--dnsname',
            type=str,
            required=False,
            help='OpenRemote dns',
            default='staging.demo.openremote.io',
        )
        parser.add_argument(
            '--realm',
            required=False,
            type=str,
            help='realm to work on',
            default='master',
        )
        parser.add_argument(
            '--delay',
            type=int,
            help='delay between steps in test scenarios',
            default=1,
        )
        parser.add_argument(
            '--no-quit', action='store_true', help='open browser and login'
        )
        parser.add_argument(
            '-n',
            '--dry-run',
            action='store_true',
            help='showing effects without actual run and exit',
        )
        parser.add_argument(
            '-v',
            '--verbose',
            action='count',
            default=0,
            help='increase output verbosity',
        )
        parser.add_argument(
            '--no-quiet', action='store_true', help='suppress info'
        )
        args = parser.parse_args(sys.argv[1:])
        # if args.no_quiet:
        config.QUIET = not args.no_quiet
        config.DRY_RUN = args.dry_run
        config.LEVEL = {
            0: logging.ERROR,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG,
        }.get(args.verbose, logging.DEBUG)
        logging.getLogger().setLevel(config.LEVEL)

        logging.info(args)
        if not args.password:
            try:
                args.password = os.getenv('SETUP_ADMIN_PASSWORD')
            except:
                raise Exception("No password given")
        if args.password:
            logging.info(
                f'setting password for user {args.user!r} at {args.dnsname!r} in realm {args.realm!r}'
            )
            config.set_password(
                url=args.dnsname, username=args.user, password=args.password
            )

        url = args.dnsname
        user = args.user
        delay = args.delay
        quit = not args.no_quit
    else:
        url = 'staging.demo.openremote.io'
        user = 'admin'
    print(f"0. Login into {url}")
    driver = _manager_ui_login(url, user, realm='master')
    _manager_ui_wait_map(driver, url)
    # test plan document https://docs.google.com/document/d/1RVt47Y9KLJl_YSNwoLrOE3VNWfUm2VaOpZzS7tebItI/edit
    print("1. Go to the 'Assets' page in the webapp")
    time.sleep(delay)
    driver.go_to(f'https://{url}/manager/#!assets')
    print(
        "2. Open the add asset dialog by clicking the '+' icon in the asset tree on the left."
    )
    time.sleep(delay)
    _manager_ui_add_asset_dialog(driver, url)
    print("3. Give the asset the name 'Weather Agent'")
    time.sleep(delay)
    _manager_ui_add_http_weather_agent(driver, url)
    print("4. and select the asset type 'HTTP Client Agent' from the list.")
    time.sleep(delay)
    _manager_ui_select_http_agent(driver, url)
    print("5. Press 'Add'")
    time.sleep(delay)
    _manager_ui_press_add(driver, url)
    print(
        "6. First we set the Base URI of the weather service that we will use for further queries. TODO"
    )
    if quit:
        # Need this for manager to act (maybe some confirmation TODO)
        time.sleep(1)
    else:
        input('Press ENTER to quit')
