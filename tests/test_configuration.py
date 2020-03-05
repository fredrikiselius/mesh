from configparser import ConfigParser
import os

import pytest

from mesh.configuration import Configuration, _REQUIRED_ATTRIBUTES
from mesh.exceptions import InvalidConfiguration


@pytest.fixture
def required_attrs():
    return _REQUIRED_ATTRIBUTES


@pytest.fixture
def base_configparser():
    config_parser = ConfigParser()

    config_parser.add_section('plex')
    config_parser.set('plex', 'serveridentifier', 'test')
    config_parser.set('plex', 'serverownertoken', 'test')

    config_parser.add_section('trakt')
    config_parser.set('trakt', 'clientid', 'test')
    config_parser.set('trakt', 'clientsecret', 'test')
    return config_parser


@pytest.fixture
def valid_config_file(tmp_path, base_configparser):
    path = os.path.join(tmp_path, 'config')
    with open(path, 'w') as f:
        base_configparser.write(f)
    return path


@pytest.fixture()
def invalid_key_config_file(tmp_path, base_configparser):
    base_configparser.set('plex', '__dict__', 'test')
    path = os.path.join(tmp_path, 'config')
    with open(path, 'w') as f:
        base_configparser.write(f)
    return path


@pytest.fixture()
def missing_key_file(tmp_path, base_configparser):
    base_configparser.remove_option('plex', 'serveridentifier')
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


def test_configuration_from_valid_file(valid_config_file, required_attrs):
    config = Configuration(valid_config_file)
    for attr in required_attrs:
        assert getattr(config, attr) == 'test'


def test_configuration_with_invalid_keys(invalid_key_config_file):
    with pytest.raises(InvalidConfiguration):
        config = Configuration(invalid_key_config_file)


def test_configuration_from_invalid_file(invalid_file):
    with pytest.raises(InvalidConfiguration):
        config = Configuration(invalid_file)


def test_configuration_with_missing_keys(missing_key_file):
    with pytest.raises(InvalidConfiguration):
        config = Configuration(missing_key_file)
