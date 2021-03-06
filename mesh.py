"""This is the entry point into the Mesh application"""

import argparse
import logging
import sys

from mesh.configuration import get_config
from mesh.interactive import first_run_setup


def setup_args():
    """Initialize the CLI argument parser"""

    parser = argparse.ArgumentParser(
            prog='Mesh',
            description='Two-way synchronization between Plex and Trakt')
    parser.add_argument(
            '--log_level',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            default='warning')
    return parser.parse_args()


def setup_logging(level):
    """Initialize logging"""

    logging.basicConfig(level=logging.getLevelName(level.upper()))


def run():
    """Run the application"""

    args = setup_args()
    setup_logging(args.log_level)

    config = get_config()
    if config.is_new:
        print('A new config file has been generated. Fill in the missing '
              'fields and rerun the application')
        # sys.exit()
        identifier, token = first_run_setup()
        config.plex_serveridentifier = identifier
        config.plex_serverownertoken = token
        config.save()

run()
