import logging
import urllib3

import plexapi
from plexapi.exceptions import BadRequest
from plexapi.myplex import MyPlexAccount
from plexapi.config import reset_base_headers
import requests

logger = logging.getLogger(__name__)


def owned_servers(username, password):
    """Returns basic information about all owned servers

    Fetches the name, identifier and token for each owned server.
    If no servers are found, or if user authentication fails,
    an empty list is returned.

    :param username: Plex account username
    :param password: Plex account password
    :type username: :class:`~python:str`
    :type password: :class:`~python:str`
    :return: Name, identifier and token for each owned server
    :rtype: :class:`~python:list` [ :class:`~python:tuple`
            [ :class:`~python:str` ] ]
    """

    servers = []
    try:
        plex_acc = MyPlexAccount(username, password)
        for resource in plex_acc.resources():
            if resource.provides == 'server' and resource.owned:
                servers.append((resource.name,
                               resource.clientIdentifier,
                               resource.accessToken))
    except BadRequest as e:
        logging.exception(f'Failed to authenticate user "{username}"')
        pass
    return servers




# Format ready authorization url
AUTH_URL = f'https://app.plex.tv/auth#?' \
              'context[device][product]={product}&' \
              'context[device][environment]=bundled&' \
              'context[device][layout]=desktop&' \
              'context[device][platform]={platform}&' \
              'context[device][device]={product} ({platform})&' \
              'clientID={client_id}&' \
              'code={code}'

# Pin Url
PIN_URL = 'https://plex.tv/api/v2/pins'

AUTH_HEADERS = ('X-Plex-Product', 'X-Plex-Platform', 'X-Plex-Device', 'X-Plex-Client-Identifier')


def build_auth_headers(product, platform, client_identifier):
    """Returns a dict with auth headers

    :param product: The name of the product
    :param platform: The platform type (iOS, Android, Web, etc)
    :param client_identifier: Unique identifier
    """

    from plexapi import reset_base_headers
    import plexapi

    plexapi.X_PLEX_PRODUCT = 'Mesh'

    all = reset_base_headers()
    headers = {h: all[h] for h in AUTH_HEADERS}
    print(headers)
    return headers


def oauth(product_name, client_identifier, platform='Web'):
    """ Retrive plex token from user with authenticate

    https://github.com/tidusjar/Ombi/issues/2894#issuecomment-477404691

    :return: Plex token for the authenticated user
    :rtype: Str or None
    """
    headers = build_auth_headers(product_name, platform, client_identifier)
    with requests.session() as session:
        response = session.post('https://plex.tv/api/v2/pins.json',
                                headers=headers,
                                params={'strong': True})

        if response.status_code != requests.codes.created:
            logger.debug('Failed to create authentication for client')
            return None

        data = response.json()

        url = AUTH_URL.format(product=product_name, platform=platform,
                              client_id=client_identifier, code=data['code'])

        yield url
        response = session.get(PIN_URL + '/' + str(data["id"]) + '.json', headers=headers)
        if response.status_code != requests.codes.ok:
            logger.warning('Failed to retrieve authentication token (status code: {code})'.format(response.status_code))
            yield None

        token = response.json().get('authToken')
        if token is None:
            logger.warning('Failed to retrieve authentication token. Token entry empty')
            yield None

        response = session.get('https://plex.tv/users/account.json', headers={'X-Plex-Token': token})
        if response.status_code != requests.codes.ok:
            logger.warning('Failed to retrieve username')
            yield None

        yield response.json()['user']['username'], token


if __name__ == '__main__':
    import uuid
    auth = oauth('mest', str(uuid.getnode()))
    print(next(auth))
    input('Press ENTER')
    print(next(auth))