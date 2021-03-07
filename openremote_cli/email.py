#!/usr/bin/python3

import smtplib
import sys
import logging
import argparse

from openremote_cli import config


def sendmail(receiver, subject, message_text, smtp_user, smtp_password):

    message = '\r\n'.join(
        [
            f'From: no-reply@openremote.io',
            f'To: {receiver}',
            f'Subject: {subject}',
            message_text,
        ]
    )

    try:
        server = smtplib.SMTP(config.SMTP_SERVER, 587)
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)

        server.sendmail('no-reply@openremote.io', [receiver], message)
        logging.debug('Successfully sent email')
    except Exception as error:
        logging.error(error)
        logging.debug('Error: unable to send email')


def main():
    parser = argparse.ArgumentParser(
        description='Sends e-mail with given SMTP credentials'
    )
    parser.add_argument('user', help='SMTP User ID. e.g. AKI...')
    parser.add_argument('password', help='SMTP password')
    parser.add_argument(
        '-t',
        '--to',
        help='Email receiver',
        required=False,
        default='no-reply@openremote.io',
    )
    parser.add_argument(
        '--subject', help='Email subject', required=False, default='Test mail'
    )
    parser.add_argument('--message', help='Email message body', required=False)

    args = parser.parse_args()
    if not args.message:
        args.message = f"""
    This is a test e-mail message from {args.sender} to {args.to} via AWS.

    User: {args.user}
    Password: {args.password}
    """

    sendmail(
        args.sender,
        args.to,
        args.subject,
        args.message,
        args.user,
        args.password,
    )


if __name__ == '__main__':
    config.initialize()
    main()
