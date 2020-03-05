"""This module contains various CLI interaction methods"""

from plexapi import X_PLEX_IDENTIFIER, X_PLEX_PLATFORM

from mesh.plex import owned_servers, oauth


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
    auth = oauth('Mesh', X_PLEX_IDENTIFIER, X_PLEX_PLATFORM)
    print('Browse to the following url and login:')
    print(next(auth))
    input('Press ENTER to continue')

    user_token_pair = next(auth)
    if user_token_pair is None:
        print('Authentication failed')
        return None
    print(f'User {user_token_pair[0]} has successfully authenticated')
    return user_token_pair


if __name__ == '__main__':
    plex_oauth()