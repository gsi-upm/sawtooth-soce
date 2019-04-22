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

import sys
import os
import argparse
import pkg_resources

from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging
from sawtooth_sdk.processor.log import log_configuration
from sawtooth_sdk.processor.config import get_log_config
from sawtooth_sdk.processor.config import get_log_dir
from sawtooth_sdk.processor.config import get_config_dir
from sawtooth_soce.processor.handler import SoceTransactionHandler
from sawtooth_soce.processor.config.soce import SOCEConfig
from sawtooth_soce.processor.config.soce import \
    load_default_soce_config
from sawtooth_soce.processor.config.soce import \
    load_toml_soce_config
from sawtooth_soce.processor.config.soce import \
    merge_soce_config


DISTRIBUTION_NAME = 'sawtooth-soce'


def load_soce_config(first_config):
    default_soce_config = \
        load_default_soce_config()
    conf_file = os.path.join(get_config_dir(), 'soce.toml')

    toml_config = load_toml_soce_config(conf_file)

    return merge_soce_config(
        configs=[first_config, toml_config, default_soce_config])


def create_soce_config(args):
    return SOCEConfig(connect=args.connect)


def parse_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-C', '--connect',
        help='Endpoint for the validator connection')

    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='Increase output sent to stderr')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='print version information')

    return parser.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    processor = None
    try:
        arg_config = create_soce_config(opts)
        soce_config = load_soce_config(arg_config)
        #URL of the validator's container tcp://127.0.0.1:4004
        processor = TransactionProcessor(url=soce_config.connect)
        log_config = get_log_config(filename="soce_log_config.toml")

        # If no toml, try loading yaml
        if log_config is None:
            log_config = get_log_config(filename="soce_log_config.yaml")

        if log_config is not None:
            log_configuration(log_config=log_config)
        else:
            log_dir = get_log_dir()
            # use the transaction processor zmq identity for filename
            log_configuration(
                log_dir=log_dir,
                name="soce-" + str(processor.zmq_id)[2:-1])

        init_console_logging(verbose_level=opts.verbose)

        handler = SoceTransactionHandler()

        processor.add_handler(handler)

        processor.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:  # pylint: disable=broad-except
        print("Error: {}".format(e))
    finally:
        if processor is not None:
            processor.stop()
