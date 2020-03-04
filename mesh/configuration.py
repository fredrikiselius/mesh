import configparser
import logging
import os

from mesh.exceptions import InvalidConfiguration

logger = logging.getLogger(__name__)

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_PATH, 'config')

#: Required configuration keys (**must** exist in the external config file).
_REQUIRED_ATTRIBUTES = (
        'clientid',
        'clientsecret',
        'serveridentifier',
        'serverownertoken',
)


class Configuration:
    """Application configuration data class

    Reads the application configuration from the file given by *path*.
    If *path* doesn't point to an existing file a new one is generated.
    Otherwise, the existing one is loaded.
    Each configuration key given by the file is added as a instance attribute.



    .. warning:: This data class should be considered as read-only and
                 never be instantiated explicitly.
                 :data:`mesh.configuration.config` should be used instead.

    :param path: Full path to the config file
    :type path: :class:`~python:str`
    """

    def __init__(self, path):
        #: Path to the configuration file
        self._path = path

        #: Whether or not the configuration file is newly generated
        self.is_new = False

        if not os.path.exists(path):
            logger.warning('Configuration file does not exist. '
                           'Generating new...')
            self._generate()
        else:
            self._load()

    def _generate(self):
        """Generates a new configuration file"""

        config_parser = configparser.ConfigParser()

        config_parser.add_section('trakt')
        config_parser.set('trakt', 'clientid', '')
        config_parser.set('trakt', 'clientsecret', '')

        config_parser.add_section('plex')
        config_parser.set('plex', 'ServerIdentifier', '')
        config_parser.set('plex', 'ServerOwnerToken', '')

        with open(self._path, 'w') as f:
            config_parser.write(f)
        self.is_new = True

    def _load(self):
        """Loads the configuration file

        Adds all configuration keys as instance attributes with their
        corresponding values.

        :raises: :class:`mesh.exceptions.InvalidConfiguration`
                 if duplicate configuration keys are encountered
                 or if the configurations is missing a required key.
        """

        config_parser = configparser.ConfigParser()

        try:
            config_parser.read(self._path)
        except configparser.ParsingError as e:
            logger.exception(f'Failed to parse "{self._path}"', exc_info=e)
            raise InvalidConfiguration('Unable to parse file') from e

        attrs = []
        for section in config_parser.sections():
            for key in config_parser[section]:
                if hasattr(self, key):
                    logger.error(f'"{key}" is already an attribute of '
                                 f'Configuration')
                    raise InvalidConfiguration(f'Invalid key "{key}"')

                logger.debug(f'Setting attribute "{key}" to '
                             f'"{config_parser[section][key]}"')
                setattr(self, key, config_parser[section][key])
                attrs.append(key)

        if not all([r_attr in attrs for r_attr in _REQUIRED_ATTRIBUTES]):
            raise InvalidConfiguration('Missing required configuration key')


def get_config(path=None):
    global _config

    if path is None:
        path = CONFIG_PATH

    if _config is None:
        _config = Configuration(path)
    return _config


#: Instantiated :class:`Configuration` object.
#: Should **always** be used when configuration settings are required.
_config = None
