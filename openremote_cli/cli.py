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

from openremote_cli import config
from openremote_cli import scripts

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# TODO make telemetry user configurable
ENABLE_TELEMETRY = True


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
            1: logging.ERROR,
            2: logging.WARNING,
            3: logging.INFO,
            4: logging.DEBUG,
        }.get(args.verbosity, logging.DEBUG)
        logging.getLogger().setLevel(config.LEVEL)

        if args.dry_run is True:
            logging.warning('Enabling dry run mode')
            config.DRY_RUN = True

        logging.debug(args)
        logging.debug(unknown)

        if ENABLE_TELEMETRY:
            send_metric(arguments)

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
                # use dispatch pattern to invoke method with same name so it's
                # easy to add new subcommands
                logging.debug('dispatching ' + command)
                getattr(self, command)(arguments)

    # Basic command run without arguments adds parser
    def help(self, arguments=[]):
        if len(arguments) > 0:
            self.base_subparser.parse_args(['-h'])
        else:
            self.__parser('help', 'CLI help')

    def hello(self, arguments=[]):
        if len(arguments) > 0:
            args = self.base_subparser.parse_args(arguments)
            print('Hello ' + args.name)
        else:
            parser = self.__parser('hello', 'Sample command')
            parser.add_argument(
                '-n',
                '--name',
                type=str,
                default='World',
                help='Optional flag to be more friendly',
            )

    def deploy(self, arguments=[]):
        if len(arguments) > 0:
            args = self.base_subparser.parse_args(arguments)
            logging.debug(args)
            if args.action == 'create':
                print(
                    'Deploying OR... This can take few minutes, be patient.\n'
                )
                scripts.deploy(args.password)
            elif args.action == 'remove':
                print('Removing OR stack...\n')
                scripts.remove()
            elif args.action == 'clean':
                print('Cleaning OR resources...\n')
                scripts.clean()
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
                choices=['create', 'remove', 'clean'],
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
            # parser.add_argument("-u", type=str, default="secret")

    def __parser(self, name, description):
        parser = self.subparsers.add_parser(
            name=name, description=description, help=description
        )
        return self._add_std_arguments(parser)

    def _add_std_arguments(self, parser):
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
            default=1,
            help="increase output verbosity",
        )
        return parser


def send_metric(cli_input):
    # TODO capture exit reason and duration
    payload = {
        "metrics": [
            {
                "userId": os.getlogin(),
                "osPlatform": platform.system(),
                "osVersion": platform.version(),
                "pythonVersion": sys.version,
                "command": {
                    "input": " ".join(cli_input),
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


def main():
    config.initialize()
    OpenRemote(sys.argv[1:])


# Support invoking the script directly from source
if __name__ == '__main__':
    exit(main())
