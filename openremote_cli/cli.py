# -*- coding: utf-8 -*-
import argparse
import sys
import pkg_resources
import logging
import inspect
import os
import getpass
import platform
from datetime import datetime
import requests
import time

# For checking version
# TODO check if urllib can be replaced with requests or other way around
import urllib.request
import json

from openremote_cli import config
from openremote_cli import scripts
from openremote_cli import gen_aws_smtp_credentials

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class OpenRemote(object):
    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog='openremote-cli')

        self.base_subparser = self._add_std_arguments(parser)

        # Create subparsers
        self.subparsers = parser.add_subparsers(
            title='command', dest='command'
        )
        for attr in dir(self):
            if inspect.ismethod(getattr(self, attr)) and attr[0] != '_':
                getattr(self, attr)([])

        args, unknown = self.base_subparser.parse_known_args(arguments)
        if args.quiet:
            config.QUIET = True
            args.verbosity = 0

        config.LEVEL = {
            0: logging.ERROR,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG,
        }.get(args.verbosity, logging.DEBUG)
        logging.getLogger().setLevel(config.LEVEL)

        if args.no_telemetry:
            config.TELEMETRY = False

        if args.dry_run is True:
            logging.info('Enabling dry run mode')
            config.DRY_RUN = True
        if args.verbosity > 0:
            config.VERBOSE = True

        logging.debug(args)

        # handle no arguments
        if len(arguments) == 0:
            self.help(['--help'])
        else:
            command = args.command
            logging.debug(f"command: {command}")
            # handle undefined command
            if not command:
                self.help(arguments)
            elif not hasattr(self, command):
                if command[0] != '-':
                    print('Unknown command ' + command)
                self.help(arguments)
            else:
                if not config.QUIET:
                    if config.DRY_RUN:
                        print("--dry-run active!")
                    if not config.VERBOSE:
                        print(
                            "To see commands use -v switch (-vvv for debug)\n"
                        )
                    else:
                        print(
                            'If you need help go to https://forum.openremote.io/\n'
                        )
                    # use dispatch pattern to invoke method with same name so it's
                    # easy to add new subcommands
                    logging.debug('dispatching ' + command + f'({arguments})')
                getattr(self, command)(arguments)

    # Basic command run without arguments adds parser
    def help(self, arguments=[]):
        if len(arguments) > 0:
            self.base_subparser.parse_args(['-h'])
        else:
            pass
            # parser = self.__parser('help', 'CLI help')

    def configure_aws(self, arguments=[]):
        if len(arguments) > 0:
            args = self.base_subparser.parse_args(arguments)
            logging.debug(args)
            if args.id:
                scripts.configure_aws(args.id, args.secret, args.region)
            else:
                print(
                    gen_aws_smtp_credentials.calculate_key(
                        args.secret, config.REGION
                    ),
                    end='',
                )
        else:
            parser = self.__parser(
                'configure_aws', 'configure AWS credentials'
            )
            arguments = parser.add_argument_group("configure_aws arguments")
            arguments.add_argument(
                "-i",
                "--id",
                type=str,
                required=False,
                help="Access key ID (if not given then return SMTP password)",
            )
            arguments.add_argument(
                "-s",
                "--secret",
                type=str,
                required=True,
                help="Secret access key",
            )
            arguments.add_argument(
                "-r",
                "--region",
                type=str,
                required=False,
                help="AWS Region",
                default="eu-west-1",
            )

    def map(self, arguments=[]):
        if len(arguments) > 0:
            args = self.base_subparser.parse_args(arguments)
            logging.debug(args)
            if args.action == 'list':
                scripts.map_list()
            elif args.action == 'upload':
                scripts.map_upload(args.f)
            elif args.action == 'download':
                scripts.map_download(args.f)
            elif args.action == 'delete':
                scripts.map_delete(args.f)
            else:
                raise ValueError(f"'{args.action}' not implemented")
        else:
            parser = self.__parser('map', 'map storage/retrieve service')
            arguments = parser.add_argument_group("map arguments")
            arguments.add_argument(
                '-a',
                '--action',
                nargs="?",
                choices=['list', 'upload', 'download', 'delete'],
                help='list/upload/download/delete map from S3, defaults to "list"',
                default='list',
            )
            arguments.add_argument('-f', type=str, help="file name")

    def deploy(self, arguments=[]):
        if len(arguments) > 0:
            args = self.base_subparser.parse_args(arguments)
            logging.debug(args)
            if args.action == 'create':
                print(
                    'Deploying OR... This usually takes less than 15 minutes.\n'
                )
                if args.provider == 'aws':
                    scripts.deploy_aws(args.password, args.dnsname)
                else:
                    smtp_user, smtp_password = None, None
                    if args.with_email:
                        logging.debug('Creating SMTP credentials')
                        smtp_user, smtp_password = scripts.smtp_credentials(
                            args.dnsname
                        )
                        logging.debug(
                            f'user: {smtp_user}, password: {smtp_password}'
                        )
                    scripts.deploy(args.password, smtp_user, smtp_password)
            elif args.action == 'remove':
                print('Removing OR stack...\n')
                if args.provider == 'aws':
                    scripts.remove_aws(args.dnsname)
                else:
                    scripts.remove()
            elif args.action == 'clean':
                print('Cleaning OR resources...\n')
                if args.provider == 'aws':
                    scripts.remove_aws(args.dnsname)
                else:
                    scripts.clean()
            elif args.action == 'health':
                scripts.deploy_health(args.dnsname, args.verbosity)
            else:
                raise ValueError(f"'{args.action}' not implemented")
        else:
            logging.debug('adding deploy parser')
            parser = self.__parser(
                'deploy',
                'Deploy OpenRemote stack. By default create on localhost.',
            )
            arguments = parser.add_argument_group("deploy arguments")
            arguments.add_argument(
                '-a',
                '--action',
                nargs="?",
                choices=['create', 'remove', 'clean', 'health'],
                help='create/remove/clean OpenRemote stack, defaults to "create"',
                default='create',
            )
            arguments.add_argument(
                '-p',
                '--password',
                type=str,
                default='secret',
                help='password for admin user, defaults to "secret"',
            )
            arguments.add_argument(
                '--provider',
                nargs="?",
                choices=['aws', 'localhost'],
                default='localhost',
                help='defaults to "localhost"',
            )
            arguments.add_argument(
                '--dnsname',
                type=str,
                help='host and domain name, defaults to "localhost"',
                default='localhost',
            )
            arguments.add_argument(
                '--with-email',
                action='store_true',
                help='generate valid SMTP server access keys',
            )

    def perquisites(self, arguments=[]):
        if len(arguments) > 0:
            args = self.base_subparser.parse_args(arguments)
            logging.debug(args)
            if args.install is True:
                print('Checking and installing missing tools.\n')
                logging.error("Not implemented")
            else:
                print('Checking for required tools')
                scripts.check_tools()
        else:
            logging.debug('adding perquisites parser')
            parser = self.__parser(
                'perquisites', 'Check if all required tools are installed'
            )
            arguments = parser.add_argument_group("perquisites arguments")
            arguments.add_argument(
                '--install', action='store_true', help='install missing tools'
            )

    def __parser(self, name, description):
        parser = self.subparsers.add_parser(
            name=name, description=description, help=description
        )
        return self._add_std_arguments(parser)

    def _add_std_arguments(self, parser):
        parser.add_argument(
            '-V',
            '--version',
            action='version',
            version=f'%(prog)s/{package_version()} {sys.version} {platform.system()}/{platform.version()}',
        )
        parser.add_argument(
            '-n',
            '--dry-run',
            action='store_true',
            help='showing effects without actual run and exit',
        )
        parser.add_argument(
            '-v',
            '--verbosity',
            action='count',
            default=0,
            help='increase output verbosity',
        )
        parser.add_argument(
            '-t',
            '--no-telemetry',
            action='store_true',
            help="Don't send usage data to server",
        )
        parser.add_argument(
            '-q', '--quiet', action='store_true', help='suppress info'
        )
        return parser


def send_metric(cli_input, exit_reason, exit_code, duration):
    input_cmd = " ".join(cli_input)
    if 'configure_aws' in input_cmd:
        # never telemetry secrets!
        return
    try:
        user_id = f'{getpass.getuser()}'
    except:
        # We don't have login in github workflow
        user_id = 'No login!'
    payload = {
        "metrics": [
            {
                "userId": user_id,
                "cliVersion": f'{package_version()}',
                "osPlatform": platform.system(),
                "osVersion": platform.version(),
                "pythonVersion": sys.version,
                "command": {
                    "input": input_cmd,
                    "exitReason": exit_reason,
                    "exitCode": exit_code,
                    "duration": duration,
                    "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                },
            }
        ]
    }

    try:
        requests.post(config.TELEMETRY_URL, json=payload, timeout=2000)
    except requests.exceptions.RequestException as exception:
        logging.debug(str(exception))


def package_version():
    return pkg_resources.get_distribution('openremote_cli').version


def isLatestVersion():
    if config.QUIET:
        return
    # Check PyPI for the latest version number
    contents = urllib.request.urlopen(
        'https://pypi.org/pypi/openremote-cli/json'
    ).read()
    data = json.loads(contents)
    latest_version = data['info']['version']
    if latest_version != package_version():
        print(
            f'\nyour version ({package_version()}) < PyPI version ({latest_version}). Consider\npip3 install --upgrade openremote-cli'
        )


def main():
    config.initialize()
    exit_reason = "program finished normally"
    exit_code = 0
    start = time.time()
    try:
        OpenRemote(sys.argv[1:])
    except Exception as error:
        exit_reason = str(error)
        exit_code = -1
    finally:
        end = time.time()
        if (
            config.TELEMETRY
            and '--no-telemetry' not in sys.argv
            and '-t' not in sys.argv
        ):
            logging.debug(f'Sending telemetry to {config.TELEMETRY_URL}')
            send_metric(sys.argv[1:], exit_reason, exit_code, end - start)
        else:
            logging.debug(f'skipping telemetry: {exit_reason}')
        # Check if there is a new version on PyPI
        isLatestVersion()


# Support invoking the script directly from source
if __name__ == '__main__':
    exit(main())
