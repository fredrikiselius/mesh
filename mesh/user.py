from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from mesh.helpers import datetime_to_ISO8601_str, datetime_from_ISO8601_str


@dataclass
class User:
    """Dataclass for holding specific user data

    :param name: The user's Plex name
    :param token: Access token to the user's Plex account
    :param trakt: Trakt authentication response
    :param last_pull: Last time user pulled from trakt
    :param last_push: Last time user pushed to trakt
    :param last_sync: Last time user performed a full sync
    :param url: The url through which the user managed to connect to the plex
                server during the last pull/push/sync
    """

    name: str
    token: str
    trakt: dict = field(repr=False)

    last_pull: datetime = field(
        default_factory=lambda: datetime.min.replace(tzinfo=timezone.utc)
    )

    last_push: datetime = field(
        default_factory=lambda: datetime.min.replace(tzinfo=timezone.utc)
    )

    last_sync: datetime = field(
        default_factory=lambda: datetime.min.replace(tzinfo=timezone.utc)
    )
    url: str = ''

    def __post_init__(self):
        if isinstance(self.last_pull, str):
            self.last_pull = datetime_from_ISO8601_str(self.last_pull)

        if isinstance(self.last_push, str):
            self.last_push = datetime_from_ISO8601_str(self.last_push)

        if isinstance(self.last_sync, str):
            self.last_sync = datetime_from_ISO8601_str(self.last_sync)

    @classmethod
    def from_json(cls, data):
        return cls(**data)


@dataclass
class UserManager:
    """This class gives access to the different users in the application

    Also handles the saving and loading of the users file. On creation it is
    assumed that the parent folder of the given file exists.

    :param file: Full path to the usermapping file
    :param users: List of all the users
    """
    file: Path
    users: list = field(default_factory=list)

    def __post_init__(self):
        if self.file.exists():
            self._load()

    def _load(self):
        """Loads a UserManager from a json file"""
        with self.file.open() as f:
            self.users = list(map(User.from_json, json.load(f).get('users')))

    def add(self, user):
        """Adds a user

        :param user: The user to be added
        :raises: ValueError if a user of the same name is already managed
        """

        if self.get(user.name) is not None:
            raise ValueError(f'User "{user.name}" already exists')
        self.users.append(user)

    def get(self, username):
        """Returns the user with matching name or None"""
        return next(filter(lambda u: u.name == username, self.users), None)

    def save(self):
        """Saves the UserManager as json"""
        with self.file.open(mode='w') as f:
            json.dump(self, f, cls=UserEncoder, indent=2)


class UserEncoder(json.JSONEncoder):
    """Json encoder for dataclasses and datetime objects

    If the given object is a dataclass asdict() will be called.
    On datetime objects, datetime_to_ISO8601_str is used.

    """

    def default(self, o):
        """Returns serialized version of datetime and dataclass"""

        if is_dataclass(o):
            return asdict(o)

        if isinstance(o, datetime):
            return datetime_to_ISO8601_str(o)

        if isinstance(o, Path):
            return str(o)
        return json.JSONEncoder.default(self, o)