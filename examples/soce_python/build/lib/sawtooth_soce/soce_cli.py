# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from __future__ import print_function

import argparse
import getpass
import logging
import os
import traceback
import sys
import pkg_resources

from colorlog import ColoredFormatter

from sawtooth_soce.soce_client import SoceClient
from sawtooth_soce.soce_exceptions import SoceException


DISTRIBUTION_NAME = 'sawtooth-soce'


DEFAULT_URL = 'http://127.0.0.1:8008'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def add_create_voter(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'create-voter',
        help='Creates a new voting',
        description='Sends a transaction to start an soce voting with the '
        'identifier <name>. This transaction will fail if the specified '
        'game already exists.',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='unique identifier for the new game')

    parser.add_argument(
        'preferences',
        type=str,
        help='unique identifier for the new game')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for game to commit')


def add_create_voting(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'create-voting',
        help='Displays information for all soce votings',
        description='Displays information for all soce votings in state',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='unique identifier for the new game')

    parser.add_argument(
        'configurations',
        type=str,
        help='unique identifier for the new game')
    
    parser.add_argument(
        'sc_method',
        type=str,
        help='unique identifier for the new game')
    
    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for game to commit')

def add_register_voter(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'register-voter',
        help='Displays information about an soce voting',
        description='Displays the soce voting <name>',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='identifier for the game')

    parser.add_argument(
        'voter_id',
        type=str,
        help='identifier for the game')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for game to commit')

def add_apply_voting_method(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'apply-voting-method',
        help='Sums a value',
        description='Sends a transaction to sum a square in the soce game '
        'with the identifier <name>. This transaction will fail if the '
        'specified game does not exist.',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='identifier for the game')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for sum transaction '
        'to commit')



def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to make votings '
        'by sending SOCE transactions.',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_create_voter(subparsers, parent_parser)
    add_create_voting(subparsers, parent_parser)
    add_register_voter(subparsers, parent_parser)
    add_apply_voting_method(subparsers, parent_parser)

    return parser


def do_create_voter(args):
    name = args.name
    preferences = args.preferences

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = SoceClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.create_voter(
            name, preferences, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.create_voter(
            name, preferences,
            auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))

def do_create_voting(args):

    name = args.name
    configurations = args.configurations
    sc_method = args.sc_method

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = SoceClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.create_voting(
            name, configurations, sc_method, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.create_voting(
            name, configurations, sc_method,
            auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))


def do_register_voter(args):
    name = args.name
    voter_id = args.voter_id

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = SoceClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.register_voter(
            name, voter_id, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.register_voter(
            name, voter_id,
            auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))

def do_apply_voting_method(args):
    name = args.name

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = SoceClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.apply_voting_method(
            name, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.apply_voting_method(
            name,
            auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))

def _get_url(args):
    return DEFAULT_URL if args.url is None else args.url


def _get_keyfile(args):
    username = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)


def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    if args.command == 'create-voter':
        do_create_voter(args)
    elif args.command == 'create-voting':
        do_create_voting(args)
    elif args.command == 'register-voter':
        do_register_voter(args)
    elif args.command == 'apply-voting-method':
        do_apply_voting_method(args)
    else:
        raise SoceException("invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except SoceException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
