# -*- coding: utf-8 -*-
import argparse
import sys
import pkg_resources
import logging
import inspect
import os
import platform
from datetime import datetime
import requests

# For checking version
# TODO check if urllib can be replaced with requests or other way around
import urllib.request
import json

from openremote_cli import config
from openremote_cli import scripts

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

        config.LEVEL = {
            0: logging.ERROR,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG,
        }.get(args.verbosity, logging.DEBUG)
        logging.getLogger().setLevel(config.LEVEL)

        if not args.no_telemetry:
            send_metric(arguments)

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
                if config.DRY_RUN:
                    print("--dry-run active!")
                if not config.VERBOSE:
                    print("To see commands use -v switch\n")
                # use dispatch pattern to invoke method with same name so it's
                # easy to add new subcommands
                logging.debug('dispatching ' + command + f'({arguments})')
                # logging.debug(args)
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
            scripts.configure_aws(args.id, args.secret, args.region)
        else:
            parser = self.__parser(
                'configure_aws', 'configure AWS credentials'
            )
            parser.add_argument(
                "-i", "--id", type=str, required=True, help="Access key ID"
            )
            parser.add_argument(
                "-s",
                "--secret",
                type=str,
                required=True,
                help="Secret access key",
            )
            parser.add_argument(
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
            parser = self.__parser('map', 'map storage/retrive service')
            parser.add_argument(
                '-a',
                '--action',
                nargs="?",
                choices=['configure', 'list', 'upload', 'download', 'delete'],
                help='list/upload/download/delete map from S3',
                required=True,
                const='list',
            )
            required_arguments = parser.add_argument_group(
                "configure arguments"
            )
            required_arguments.add_argument(
                "-i", "--id", type=str, required=False, help="Access key ID"
            )
            required_arguments.add_argument(
                "-s",
                "--secret",
                type=str,
                required=False,
                help="Secret access key",
            )
            required_arguments = parser.add_argument(
                '-f', type=str, help="file name"
            )

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
                    scripts.deploy(args.password)
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
            parser.add_argument(
                '-a',
                '--action',
                nargs="?",
                choices=['create', 'remove', 'clean', 'health'],
                help='create/remove/clean OpenRemote stack',
                default='create',
            )
            parser.add_argument(
                '-p',
                '--password',
                type=str,
                default='secret',
                help='Password for admin user',
            )
            parser.add_argument(
                '--provider',
                nargs="?",
                choices=['aws', 'localhost'],
                default='localhost',
            )
            parser.add_argument(
                '--dnsname',
                type=str,
                help='host and domain name',
                default='demo.mvp.openremote.io',
            )

    def perquisites(self, arguments=[]):
        if len(arguments) > 0:
            args = self.base_subparser.parse_args(arguments)
            logging.debug(args)
            if args.install is True:
                print('Checking and installing missing tools.\n')
            else:
                print('Checking for required tools')
        else:
            logging.debug('adding perquisites parser')
            parser = self.__parser(
                'perquisites', 'Check if all required tools are installed'
            )
            parser.add_argument(
                '--install',
                action='store_true',
                help='install all missing tools',
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
            '-d',
            '--dry-run',
            action='store_true',
            help='showing effects without actual run and exit',
        )
        parser.add_argument(
            "-v",
            "--verbosity",
            action="count",
            default=0,
            help="increase output verbosity",
        )
        parser.add_argument(
            "--no-telemetry",
            action='store_true',
            help="Don't send usage data to server",
        )
        return parser


def send_metric(cli_input):
    # TODO capture exit reason and duration
    input_cmd = sys.argv[0] + " " + " ".join(cli_input)
    if 'configure_aws' in input_cmd:
        # never telemetry secrets!
        return
    try:
        user_id = os.getlogin()
    except:
        # We don't have login in github workflow
        user_id = 'No login'
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
                    "exitReason": "Not Implemented",
                    "exitCode": "Not Implemented",
                    "duration": "Not Implemented",
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
    # Check pypi for the latest version number
    contents = urllib.request.urlopen(
        'https://pypi.org/pypi/openremote-cli/json'
    ).read()
    data = json.loads(contents)
    latest_version = data['info']['version']
    if latest_version != package_version():
        print(
            f'your version ({package_version()}) < PyPI version ({latest_version}). Consider\npip3 install --upgrade openremote-cli\n'
        )


def main():
    isLatestVersion()
    config.initialize()
    OpenRemote(sys.argv[1:])


# Support invoking the script directly from source
if __name__ == '__main__':
    exit(main())
