"""This module contains various CLI interaction methods"""

from collections import namedtuple

from trakt import Trakt

from mesh.plex import owned_servers, oauth
from mesh.user import User


def first_run_setup():
    print('It appears to be the first time you\'re running Mesh.', end=' ')
    print('As such, some setup is required.')
    print('(You can abort this setup anytime by pressing "Ctrl + c")')

    print('\nFirst, you must select the Plex server you wish to synchronize '
          'with Trakt.')
    print('(Neither your username nor password will be stored)\n')

    # Authentication loop
    while True:
        username = input('Enter your Plex username: ')
        password = input('Enter your Plex password ')

        servers = owned_servers(username, password)
        if not servers:
            print('Mesh was unable to locate any owned servers.')
            print('Make sure you entered the correct credentials.')
            continue
        break

    print('\nAvailable servers:')
    for i, server in enumerate(servers):
        print(f'[{i}]: {server[0]}')

    selected_server = None
    while True:
        sid = input('Enter the number of the server you wish to select: ')

        try:
            sid = int(sid)
        except ValueError:
            print(f'"{sid}" is not a valid number, try again.')
            continue

        if sid not in range(len(servers)):
            print('The selected number must be in the available range')
            continue

        print(f'Server "{servers[sid][0]}" selected')
        selected_server = servers[sid]
        break
    return selected_server[1:]


def plex_oauth():
    auth = oauth()
    print('Browse to the following url and login:')
    print(next(auth))
    input('Press ENTER to continue')

    user_token_pair = next(auth)
    if user_token_pair is None:
        print('Authentication failed')
        return None
    print(f'User {user_token_pair[0]} has successfully authenticated')
    return user_token_pair


def trakt_oauth():
    print(f'Copy the authorization pin from: {Trakt["oauth"].authorize_url("urn:ietf:wg:oauth:2.0:oob")}')
    pin = input('Enter pin: ')
    authorization = Trakt['oauth'].token_exchange(pin,
                                                  'urn:ietf:wg:oauth:2.0:oob')
    if authorization is None:
        print('Trakt authorization failed')
        return
    print('Trakt authorization successful')
    return authorization


def add_user():
    print('Adding a new user')
    print('First you need to give Mesh permission to use your plex account')
    plex_credentials = plex_oauth()
    print('')

    print('Next, you need to give Mesh permission to access your Trakt account')
    auth = trakt_oauth()
    if plex_credentials and auth:
        return User(*plex_credentials, auth)
    return None

if __name__ == '__main__':
    plex_oauth()