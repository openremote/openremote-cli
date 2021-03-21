# -*- coding: utf-8 -*-
import logging
import subprocess

from openremote_cli import config


def execute(args, no_exception=False, echo=False):
    logging.debug(f'executing command:\n\n\t{args}\n')

    if config.VERBOSE:
        print(f'> {args}')

    if config.DRY_RUN:
        return 0, 'Invoked using dry run'
    else:
        try:
            output = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                # executable='/bin/bash',
            )
        except Exception as exception:
            logging.error(f'Failed to execute {args}')
            if no_exception:
                return exception.errno, exception.strerror
            else:
                raise Exception(exception.errno, exception.strerror)
        if output.returncode != 0:
            if no_exception:
                logging.debug(f'stderr: {output.stdout}')
            else:
                logging.error(f'stderr: {output.stdout}')
                raise Exception(
                    output.returncode, output.stdout.decode('utf-8')
                )
        else:
            logging.debug(f'stdout: {output.stdout}')
        if echo and not config.QUIET:
            print(output.stdout.decode('utf-8'))
        return output.returncode, output.stdout.decode('utf-8')
