"""This is the entry point into the Mesh application"""

import argparse
import json
import logging
import os
import sys

from trakt import Trakt

from mesh.configuration import get_config
from mesh.constants import USER_MAPPING_FILE, DATA_DIR
from mesh.interactive import first_run_setup, add_user
from mesh.user import UserManager
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


def init_trakt():
    """Set id and secrect for trakt"""

    config = get_config()
    if not config.trakt.id or not config.trakt.secret:
        return False

    Trakt.configuration.defaults.client(
        id=config.trakt.id,
        secret=config.trakt.secret
    )
    return True


def quit(code=0):
    print(f'Exiting ({code})')
    sys.exit(code)


def main():
    """Run the application"""

    args = init_args()
    init_logging(args.log_level)
    init_plex()

    config = get_config()
    if config.is_new:
        identifier, token = first_run_setup()
        config.set('plex', 'identifier',  identifier)
        config.set('plex', 'token',  token)
        config.save()

    has_trakt_oauth = init_trakt()
    if not has_trakt_oauth:
        print('You must enter a valid client id and client secret for Trakt')
        print('If you do not have those, go to "https://trakt.tv/oauth/applications" and create a new application')
        quit()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    user_manager = UserManager(USER_MAPPING_FILE)

    if args.add_user:
        new_user = add_user()
        if new_user is not None:
            user_manager.add(new_user)
            user_manager.save()


if __name__ == '__main__':
    main()