from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from mesh.user import User, UserManager, UserEncoder


@pytest.fixture
def user():
    """Returns a user with name='mesh', token='token', trakt={'trakt': 'auth'}"""

    return User('mesh', 'token', {'trakt': 'auth'})


@pytest.fixture
def json_user():
    """Returns a dict with User default args"""

    return {
        'name': 'mesh',
        'token': 'token',
        'trakt': {
            'trakt': 'auth'
        }
    }


@pytest.fixture
def json_user_with_args():
    """Returns a dict with all User args"""

    return {
        'name': 'mesh',
        'token': 'token',
        'trakt': {
            'trakt': 'auth'
        },
        'last_pull': datetime.min.replace(tzinfo=timezone.utc),
        'last_push': datetime.min.replace(tzinfo=timezone.utc),
        'last_sync': datetime.min.replace(tzinfo=timezone.utc),
        'url': ''
    }


@pytest.fixture
def non_existing_file(tmp_path):
    """Returns a path to a non existing file"""
    return Path(tmp_path).joinpath('usermapping')


@pytest.fixture
def existing_file(tmp_path, json_user, json_user_with_args):
    """Returns the full path to a file containing a user manager in json format"""

    file_path = Path(tmp_path).joinpath('usermapping')

    user_manager_json = {
        'file': str(file_path),
        'users': [
            json_user,
            json_user_with_args
        ]
    }

    with file_path.open('w') as f:
        json.dump(user_manager_json, f, cls=UserEncoder)
    return file_path


def test_default_user():
    with pytest.raises(TypeError):
        u = User()


def test_user_with_required_args(user):
    assert user.name == 'mesh'
    assert user.token == 'token'
    assert user.trakt == {'trakt': 'auth'}
    assert user.last_pull == datetime.min.replace(tzinfo=timezone.utc)
    assert user.last_push == datetime.min.replace(tzinfo=timezone.utc)
    assert user.last_sync == datetime.min.replace(tzinfo=timezone.utc)
    assert user.url == ''


def test_user_from_json_with_required_args(json_user, user):
    assert user == User.from_json(json_user)


def test_user_from_json_with_all_args(json_user_with_args, user):
    assert user == User.from_json(json_user_with_args)


def test_usermanager_from_non_existing_file(non_existing_file):
    um = UserManager(non_existing_file)
    assert um.file == non_existing_file
    assert um.users == []


def test_usermanager_from_existing_file(existing_file):
    um = UserManager(existing_file)
    assert um.file == existing_file
    assert len(um.users) == 2


def test_usermanager_add_user(non_existing_file, user):
    um = UserManager(non_existing_file)
    um.add(user)
    assert um.users[0] == user


def test_usermanager_add_duplicate_user(non_existing_file, user):
    um = UserManager(non_existing_file)
    um.add(user)
    with pytest.raises(ValueError):
        um.add(user)

def test_usermanager_save(non_existing_file, user):
    um = UserManager(non_existing_file)
    um.add(user)
    um.save()

    um_load = UserManager(non_existing_file)
    assert um == um_load