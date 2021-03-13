# -*- coding: utf-8 -*-
import logging
import uuid
import wget
import json
import urllib.request
import os
import string
import requests

from keycloak import KeycloakOpenID
from random import choice, randint
from openremote_cli import shell
from openremote_cli import config
from openremote_cli import gen_aws_smtp_credentials, email


def deploy(password, smtp_user, smtp_password, dnsname):
    shell.execute('docker swarm init', no_exception=True)
    shell.execute(
        'docker volume rm openremote_postgresql-data', no_exception=True
    )
    shell.execute('docker volume create openremote_deployment-data')
    shell.execute(
        'docker run --rm -v openremote_deployment-data:/deployment openremote/deployment:mvp'
    )
    if not config.DRY_RUN:
        wget.download(
            'https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
        )
    if config.VERBOSE is True:
        print(
            '> wget -nc https://github.com/openremote/openremote/raw/master/mvp/mvp-docker-compose.yml'
        )
    env = ''
    if password != 'secret':
        env = f'SETUP_ADMIN_PASSWORD={password} '
    if smtp_user and smtp_password:
        env = (
            f'{env}SETUP_EMAIL_USER={smtp_user} '
            f'SETUP_EMAIL_PASSWORD={smtp_password} '
            f'SETUP_EMAIL_HOST=email-smtp.{config.REGION}.amazonaws.com '
        )
    if dnsname != 'localhost':
        env = f'{env}DOMAINNAME={dnsname} IDENTITY_NETWORK_HOST={dnsname} '
        # As you may be facing internet change default password for security
        generate_password, password = _password(password)
        if generate_password:
            env = f'{env}SETUP_ADMIN_PASSWORD={password} '
        # Deploy with docker-compose as proxy container does not obey
        # health check within swarm mode
        # TODO revisit proxy image to fix this, otherwise letsencrypt has problems
        shell.execute(
            f'{env}docker-compose -f mvp-docker-compose.yml -p openremote up -d'
        )
        if config.VERBOSE is True:
            print(
                '\nCheck running services with `docker ps` until containers are healthy...\n'
                f'then open https://{dnsname} and login with admin {password}\n\n'
                'Remove the stack when you are done:\n'
                '> docker-compose -f mvp-docker-compose.yml -p openremote down\n'
                '> rm mvp-docker-compose.yml\n'
            )
    else:
        shell.execute(
            f'{env}docker stack deploy -c mvp-docker-compose.yml openremote'
        )
        if config.VERBOSE is True:
            print(
                '\nCheck running services with `docker service ls` until all are 1/1 replicas...\n'
                f'then open https://localhost and login with admin {password}\n\n'
                'Remove the stack when you are done:\n'
                '> docker stack rm openremote\n'
            )
        if not config.DRY_RUN:
            os.remove(f'mvp-docker-compose.yml')
    if config.VERBOSE is True:
        print(
            '\nRemove docker resources:\n'
            "> docker images --filter 'reference=openremote/*' -q | xargs docker rmi\n"
            "> docker volume ls --filter 'dangling=true' -q | xargs docker volume rm"
        )


def deploy_health(dnsname, verbosity=0):
    try:
        health = json.loads(
            urllib.request.urlopen(
                f'https://{dnsname}/api/master/health'
            ).read()
        )
        if verbosity == 0:
            print(health['system']['version'])
        elif verbosity == 1:
            print(health['system'])
        else:
            print(health)
    except:
        if '.' not in dnsname and dnsname != 'localhost':
            host, domain = _split_dns(dnsname)
            deploy_health(f'{host}.{domain}', verbosity)
        elif verbosity == 0:
            print('0')
        else:
            print(f'Error calling\ncurl https://{dnsname}/api/master/health')


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
    stack_name = f'OpenRemote-{uuid.uuid4()}'
    check_aws_perquisites()
    generate_password, password = _password(password)
    if not config.DRY_RUN:
        wget.download(
            'https://github.com/openremote/openremote/raw/master/mvp/aws-cloudformation.template.yml'
        )
    if config.VERBOSE is True:
        print(
            '> wget -nc https://github.com/openremote/openremote/raw/master/mvp/aws-cloudformation.template.yml'
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
    # shell.execute(
    #     f'echo "aws cloudformation delete-stack --stack-name {stack_name} --profile {config.PROFILE}" > aws-delete-stack-{host}.{domain}.sh'
    # )
    # shell.execute(f'chmod +x aws-delete-stack-{host}.{domain}.sh')
    print(
        '\nStack deployed - wait about 15 min for OpenRemote installation to complete.\n'
        'Mind that running it cost money! To free resources execute:\n'
        f'aws cloudformation delete-stack --stack-name {stack_name} --profile {config.PROFILE}\n\n'
        'check running stack with health command:\n'
        f'or deploy -a health --dnsname {host}.{domain} -v'
    )


def remove_aws(dnsname):
    check_aws_perquisites()
    shell.execute(f'sh aws-delete-stack-{dnsname}.sh')
    if config.VERBOSE:
        print(f'rm aws-delete-stack-{dnsname}.sh')
    if not config.DRY_RUN:
        os.remove(f'aws-delete-stack-{dnsname}.sh')


def remove():
    shell.execute(f'docker stack rm openremote')


def clean():
    shell.execute(
        'docker volume rm --force openremote_deployment-data openremote_postgresql-data openremote_proxy-data'
    )
    shell.execute(
        'docker rmi openremote/manager-swarm openremote/deployment '
        'openremote/keycloak openremote/postgresql openremote/proxy ',
        no_exception=True,
    )
    shell.execute('docker system prune --force')


def configure_aws(id, secret, region):
    config.REGION = region
    print(
        shell.execute(
            f'aws configure set profile.{config.PROFILE}.aws_access_key_id {id}'
        )[1]
    )
    print(
        shell.execute(
            f'aws configure set profile.{config.PROFILE}.aws_secret_access_key {secret}'
        )[1]
    )
    print(
        shell.execute(
            f'aws configure set profile.{config.PROFILE}.region {region}'
        )[1]
    )


def map_upload(path):
    print(
        shell.execute(
            f'aws s3 cp {path} s3://{config.BUCKET} --profile {config.PROFILE}'
        )[1]
    )


def map_list():
    print(
        shell.execute(
            f'aws s3 ls s3://{config.BUCKET} --profile {config.PROFILE}'
        )[1]
    )


def map_download(path):
    print(
        shell.execute(
            f'aws s3 cp s3://{config.BUCKET}/{path} {path} --profile {config.PROFILE}'
        )[1]
    )


def map_delete(path):
    print(
        shell.execute(
            f'aws s3 rm s3://{config.BUCKET}/{path} --profile {config.PROFILE}'
        )[1]
    )


def check_tools():
    code, output = shell.execute('docker --version')
    if not config.QUIET:
        print(output)
    code, output = shell.execute('docker-compose --version')
    if not config.QUIET:
        print(output)
    # print('Checking AWS perquisites')
    code, output = shell.execute('aws --version')
    if not config.QUIET:
        print(output)
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
def _token(username, password, url):
    keycloak_openid = KeycloakOpenID(
        server_url=f'https://{url}/auth/',
        client_id="admin-cli",
        realm_name="master",
        client_secret_key="secret",
    )
    return keycloak_openid.token(username, password)['access_token']


def manager_login(url, username, password):
    keycloak_openid = KeycloakOpenID(
        server_url=f'https://{url}/auth/',
        client_id="admin-cli",
        realm_name="master",
        client_secret_key="secret",
    )
    response = keycloak_openid.token(username, password)
    print(json.dumps(response, indent=2))
    config.store_token(
        url, response['access_token'], response['refresh_token']
    )


def manager_list_realms(username, password, dnsname):
    response = requests.get(
        f'https://{dnsname}/auth/admin/realms',
        headers={
            'Authorization': f'Bearer ' + _token(username, password, dnsname)
        },
    )
    for r in response.json():
        if config.QUIET:
            print(f"{r['realm']}  \t{r['displayName']}")
        else:
            print(json.dumps(r, indent=2))


def manager_list_users(realm, password, dnsname):
    response = requests.get(
        f'https://{dnsname}/auth/admin/realms/{realm}/users',
        headers={
            'Authorization': f'Bearer ' + _token('admin', password, dnsname)
        },
    )
    for r in response.json():
        if config.QUIET:
            print(f"{r['username']}  \t{r['email']}")
        else:
            print(json.dumps(r, indent=2))
