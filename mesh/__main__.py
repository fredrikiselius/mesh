"""This is the entry point into the Mesh application"""

import argparse
import logging
import os
import sys


from mesh.configuration import get_config
from mesh.interactive import first_run_setup, add_user
from mesh.version import __version__


def init_args():
    """Initialize the CLI argument parser"""

    parser = argparse.ArgumentParser(
            prog='Mesh',
            description='Two-way synchronization between Plex and Trakt')
    parser.add_argument(
            '--log_level',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            default='warning')

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--pull', action='store_true', help='Pull from Trakt')
    mode.add_argument('--push', action='store_true', help='Push to Trakt')
    mode.add_argument('--sync', action='store_true', help='Two-way sync')
    mode.add_argument('--add_user', action='store_true', help='Add a new user')
    return parser.parse_args()


def init_logging(level):
    """Initialize logging"""

    logging.basicConfig(level=logging.getLevelName(level.upper()))


def init_plex():
    """Set request headers for plexapi"""

    config = get_config()
    import plexapi
    plexapi.BASE_HEADERS['X-Plex-Product'] = 'Mesh'
    plexapi.BASE_HEADERS['X-Plex-Version'] = __version__
    plexapi.BASE_HEADERS['X-Plex-Client-Identifier'] = config.mesh.identifier


def main():
    """Run the application"""

    args = init_args()
    init_logging(args.log_level)
    init_plex()

    config = get_config()
    if config.is_new:
        print('A new config file has been generated. Fill in the missing '
              'fields and rerun the application')
        # sys.exit()
        identifier, token = first_run_setup()
        config.set('plex', 'identifier',  identifier)
        config.set('plex', 'token',  token)
        config.save()

    if args.add_user:
        add_user()
    elif args.pull:
        print('pull')
    elif args.push:
        print('push')
    elif args.sync:
        print('sync')
    else:
        print('service')




if __name__ == '__main__':
    main()