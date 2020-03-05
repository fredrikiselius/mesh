import configparser
import logging
import os
import uuid

import plexapi

from mesh.exceptions import InvalidConfiguration

logger = logging.getLogger(__name__)

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_PATH, 'config')

#: Required configuration keys (**must** exist in the external config file).
_REQUIRED_ATTRIBUTES = (
        'mesh_identifier',
        'trakt_clientid',
        'trakt_clientsecret',
        'plex_serveridentifier',
        'plex_serverownertoken',
)


class Configuration:
    """Application configuration data class

    Reads the application configuration from the file given by *path*.
    If *path* doesn't point to an existing file a new one is generated.
    Otherwise, the existing one is loaded.
    Each configuration option given by the file is added as a instance
    attribute on the form *section_option*.

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

        self._config_parser = configparser.ConfigParser()

        if not os.path.exists(path):
            logger.warning('Configuration file does not exist. '
                           'Generating new...')
            self._generate()
        else:
            self._load()

    def _generate(self):
        """Generates a new configuration file"""
        for attr in _REQUIRED_ATTRIBUTES:
            section, key = attr.split('_')
            if not self._config_parser.has_section(section):
                self._config_parser.add_section(section)
            if section == 'mesh' and key == 'identifier':
                self._config_parser.set(section, key, str(uuid.uuid4()))
            else:
                self._config_parser.set(section, key, '')

        self.save()
        self.is_new = True

    def __setattr__(self, key, value):
        """Updates the config_parser if key is an config attr"""
        if key in _REQUIRED_ATTRIBUTES:
            self._config_parser.set(*key.split('_'), value)
        super(Configuration, self).__setattr__(key, value)

    def __getattr__(self, item):
        print(item in _REQUIRED_ATTRIBUTES)
        if item in _REQUIRED_ATTRIBUTES:
            return self._config_parser.get(*item.split('_'))
        return getattr(self, item)

    def _load(self):
        """Loads the configuration file

        Adds all configuration keys as instance attributes with their
        corresponding values.

        :raises: :class:`mesh.exceptions.InvalidConfiguration`
                 if duplicate configuration keys are encountered
                 or if the configurations is missing a required key.
        """

        try:
            self._config_parser.read(self._path)
        except configparser.ParsingError as e:
            logger.exception(f'Failed to parse "{self._path}"', exc_info=e)
            raise InvalidConfiguration('Unable to parse file') from e

        # attrs = []
        # for section in self._config_parser.sections():
        #     for key in self._config_parser[section]:
        #         if hasattr(self, key):
        #             logger.error(f'"{key}" is already an attribute of '
        #                          f'Configuration')
        #             raise InvalidConfiguration(f'Invalid key "{key}"')
        #
        #         attr = f'{section}_{key}'
        #         logger.debug(f'Setting attribute "{attr}" to '
        #                      f'"{self._config_parser[section][key]}"')
        #
        #         setattr(self, attr, self._config_parser[section][key])
        #         attrs.append(attr)
        #
        # if not all([r_attr in attrs for r_attr in _REQUIRED_ATTRIBUTES]):
        #     raise InvalidConfiguration('Missing required configuration key')

    def save(self):
        with open(self._path, 'w') as f:
            self._config_parser.write(f)


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