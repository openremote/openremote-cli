# -*- coding: utf-8 -*-
import logging
import subprocess

from openremote_cli import config


def execute(args):
    logging.debug(f'executing command:\n\n\t{args}\n')

    if config.VERBOSE:
        print(args)

    if config.DRY_RUN:
        return 0, 'Invoked using dry run'
    else:
        try:
            output = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                executable='/bin/bash',
            )
        except FileNotFoundError as exception:
            logging.error(f'Failed to execute {args}')
            return exception.errno, exception.strerror
        logging.debug(f'stdout: {output.stdout}')
        if output.returncode != 0:
            logging.error(f'stderr: {output.stdout}')
            raise Exception(output.returncode, output.stdout.decode('utf-8'))
        return output.returncode, output.stdout.decode('utf-8')
