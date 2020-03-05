from configparser import ConfigParser
import os

import pytest

from mesh.configuration import Configuration, _TEMPLATE
from mesh.exceptions import InvalidConfiguration


@pytest.fixture
def base_configparser():
    config_parser = ConfigParser()

    config_parser.add_section('mesh')
    config_parser.set('mesh', 'identifier', 'test')

    config_parser.add_section('plex')
    config_parser.set('plex', 'identifier', 'test')
    config_parser.set('plex', 'token', 'test')

    config_parser.add_section('trakt')
    config_parser.set('trakt', 'id', 'test')
    config_parser.set('trakt', 'secret', 'test')
    return config_parser


@pytest.fixture
def valid_config_file(tmp_path, base_configparser):
    path = os.path.join(tmp_path, 'config')
    with open(path, 'w') as f:
        base_configparser.write(f)
    return path


@pytest.fixture()
def invalid_key_config_file(tmp_path, base_configparser):
    base_configparser.add_section('__dict__')
    base_configparser.set('__dict__', 'asd', 'test')
    path = os.path.join(tmp_path, 'config')
    with open(path, 'w') as f:
        base_configparser.write(f)
    return path


@pytest.fixture()
def missing_key_file(tmp_path, base_configparser):
    base_configparser.remove_option('plex', 'identifier')
    path = os.path.join(tmp_path, 'config')
    with open(path, 'w') as f:
        base_configparser.write(f)
    return path


@pytest.fixture
def invalid_file(tmp_path):
    path = os.path.join(tmp_path, 'config')
    with open(path, 'w') as f:
        f.write('testing invalid file')
    return path


def test_configuration_from_non_existing_file(tmp_path):
    config_file = os.path.join(tmp_path, 'config')
    config = Configuration(config_file)

    assert os.path.isfile(config_file)
    assert config.is_new


def test_configuration_from_valid_file(valid_config_file):
    config = Configuration(valid_config_file)
    for s, ov in _TEMPLATE.items():
        for o in ov:
            assert getattr(getattr(config, s), o) == 'test'


def test_configuration_with_invalid_keys(invalid_key_config_file):
    with pytest.raises(InvalidConfiguration):
        config = Configuration(invalid_key_config_file)


def test_configuration_from_invalid_file(invalid_file):
    with pytest.raises(InvalidConfiguration):
        config = Configuration(invalid_file)


def test_configuration_with_missing_keys(missing_key_file):
    with pytest.raises(InvalidConfiguration):
        config = Configuration(missing_key_file)


def test_set_existing_section_valid_option(valid_config_file):
    c = Configuration(valid_config_file)
    c.set('plex', 'test', 'test')
    assert c.plex.test == 'test'


def test_set_existing_section_invalid_option(valid_config_file):
    c = Configuration(valid_config_file)
    with pytest.raises(ValueError):
        c.set('plex', '_test', 'test')


def test_set_non_existing_section(valid_config_file):
    c = Configuration(valid_config_file)
    with pytest.raises(ValueError):
        c.set('test', 'test', 'test')

