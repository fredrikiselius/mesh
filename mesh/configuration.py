from collections import namedtuple
import configparser
import logging
import os
import uuid


from mesh.exceptions import InvalidConfiguration

logger = logging.getLogger(__name__)

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_PATH, 'config')


class Configuration:
    """Application configuration data class

    Reads the application configuration from the file given by *path*.
    If *path* doesn't point to an existing file a new one is generated.
    Otherwise, the existing one is loaded.
    Each configuration section is available as an instance attribute
    which returns a :class:`~python:namedtuple` containing the options.

    :example:
    >>> config = Configuration(path_to_config)
    >>> config.plex.identifier
    >>> # Plex server identifier

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

    def __getattribute__(self, attr):
        parser = object.__getattribute__(self, '_config_parser')
        if parser.has_section(attr):
            ops, vals = zip(*parser.items(attr))
            return namedtuple(attr, ops)(*vals)
        return object.__getattribute__(self, attr)

    def _generate(self):
        """Generates a new configuration file"""
        self._config_parser.read_dict(_TEMPLATE)
        self.save()
        self.is_new = True

    def _load(self):
        """Loads the configuration file

        :raises: :class:`mesh.exceptions.InvalidConfiguration`
                 if duplicate configuration keys are encountered
                 or if the configurations is missing a required key.
                 Will also be raised if validation fails.
        """

        try:
            self._config_parser.read(self._path)
        except configparser.ParsingError as e:
            logger.exception(f'Failed to parse "{self._path}"', exc_info=e)
            raise InvalidConfiguration('Unable to parse file') from e

        status = self._validate()
        if not status.success:
            raise InvalidConfiguration(status.msg)

    def _validate(self):
        """Validates the current configuration"""
        parser = configparser.ConfigParser()
        parser.read_dict(_TEMPLATE)

        status = namedtuple('Validation', ['success', 'msg'])

        # Check is required since namedtuple is used in __getattribute__
        # (namedtuple does not allow attributes starting with _)
        for s in self._config_parser.sections():
            if any([o.startswith('_') for o in self._config_parser.options(s)]):
                return status(False, f'Options starting with _ are not allowed')

        # Assert that no internal attribute/method is overshadowed
        if any([s in self.__dir__() for s in self._config_parser.sections()]):
            return status(False, f'Forbidden section name')

        # Check that all required sections and options are available
        for s in parser.sections():
            if not self._config_parser.has_section(s):
                return status(False, f'Missing section "[{s}]"')
            for o in parser.options(s):
                if not self._config_parser.has_option(s, o):
                    return status(False, f'Missing option "[{s}] {o}"')
        return status(True, '')

    def set(self, section, option, value):
        """Sets the option in section to value

        :param section: Section name
        :param option: Option name
        :param value: Option value
        :type section: :class:`~python:str`
        :type option: :class:`~python:str`
        :type value: :class:`~python:str`
        :raises: :class:`~python:ValueError` if the option name starts with _
                 or if the section does not exist
        """

        if option.startswith('_'):
            raise ValueError('Options starting with "_" are not allowed')

        try:
            self._config_parser.set(section, option, value)
        except configparser.NoSectionError as e:
            logger.exception(e)
            raise ValueError(f'"section" must be an existing section') from e

    def save(self):
        """Saves the configuration to file"""
        with open(self._path, 'w') as f:
            self._config_parser.write(f)


_TEMPLATE = {
    'mesh': {'identifier': str(uuid.uuid4())},
    'plex': {'identifier': '',
             'token': ''},
    'trakt': {'id': '',
              'secret': ''}
}


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