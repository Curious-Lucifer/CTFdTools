import os
import re
import tempfile
import yaml

from pydantic import BaseModel, field_validator

from .ctfd import CTFd
from .utils import change_path, check_canonical, compress2zip, error, success, info


class ChallengeYamlModel(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    author: str | None = None
    connection_info: str | None = None
    flag: str | None = None
    tags: list[str] | None = None
    distfiles: list[str] | None = None
    hints: list[str] | None = None

    type: str | None = None
    value: int | dict[str, str | int] | None = None, 
    state: str | None = None

    canonical_name: str | None = None

    @field_validator('type')
    @classmethod
    def check_type(cls, v: str | None):
        if (v is not None) and (v in ['standard', 'dynamic']):
            return v
        raise ValueError('must be either `standard` or `dynamic`')

    @field_validator('state')
    @classmethod
    def check_state(cls, v: str | None):
        if (v is not None) and (v in ['hidden', 'visible']):
            return v
        raise ValueError('must be either `hidden` or `visible`')

    @field_validator('canonical_name')
    @classmethod
    def check_canonical_name(cls, v: str | None):
        if (v is not None) and re.match(r'^[a-z0-9-]+$', v):
            return v
        raise ValueError('can only contain characters a-z, 0-9, and -')


class Challenge:
    def __init__(self, 
        path: str, ctfd: CTFd, 
        yml_path: str | None = 'task.yml', 
        name: str | None = None, 
        category: str | None = None, 
        description: str = '', 
        author: str | None = None, 
        connection_info: str | None = None, 
        flag: str | None = None, 
        tags: list[str] | None = None, 
        distfiles: list[str] | None = None, 
        hints: list[str] | None = None, 
        type: str = 'standard', 
        value: int | dict[str, str | int] = 500, 
        state: str = 'hidden', 
        canonical_name: str | None = None
    ):
        self._path = path
        self._ctfd = ctfd
        self._server = self._ctfd._server

        self._name = name
        self._category = category
        self._description = description
        self._author = author
        self._connection_info = connection_info
        self._flag = flag
        self._tags = tags
        self._distfiles = distfiles
        self._hints = hints

        self._type = type
        self._value = value
        self._state = state

        self._canonical_name = canonical_name

        self._id = None

        self._yml_path = yml_path
        if self._yml_path is not None:
            self.load_yml(self._yml_path)

    def load_yml(self, yml_path: str):
        self._yml_path = yml_path

        info(f'Loading YML From {os.path.join(self._path, self._yml_path)}')
        with open(os.path.join(self._path, self._yml_path)) as f:
            y = yaml.safe_load(f)
        challenge_from_yaml = ChallengeYamlModel(**y)

        self._name = challenge_from_yaml.name if challenge_from_yaml.name is not None else self._name
        self._category = challenge_from_yaml.category if challenge_from_yaml.category is not None else self._category
        self._description = challenge_from_yaml.description if challenge_from_yaml.description is not None else self._description
        self._author = challenge_from_yaml.author if challenge_from_yaml.author is not None else self._author
        self._connection_info = challenge_from_yaml.connection_info if challenge_from_yaml.connection_info is not None else self._connection_info
        self._flag = challenge_from_yaml.flag if challenge_from_yaml.flag is not None else self._flag
        self._tags = challenge_from_yaml.tags if challenge_from_yaml.tags is not None else self._tags
        self._distfiles = challenge_from_yaml.distfiles if challenge_from_yaml.distfiles is not None else self._distfiles
        self._hints = challenge_from_yaml.hints if challenge_from_yaml.hints is not None else self._hints

        self._type = challenge_from_yaml.type if challenge_from_yaml.type is not None else self._type
        self._value = challenge_from_yaml.value if challenge_from_yaml.value is not None else self._value
        self._state = challenge_from_yaml.state if challenge_from_yaml.state is not None else self._state

        self._canonical_name = challenge_from_yaml.canonical_name if challenge_from_yaml.canonical_name is not None else self._canonical_name

    def check(self):
        if (self._name is None):
            raise ValueError('`name` not defined')
        
        if (self._category is None):
            raise ValueError('`category` not defined')
        
        if (self._type not in ['standard', 'dynamic']):
            raise ValueError('`type` should be either `standard` or `dynamic`')
        
        if (self._type == 'dynamic'):
            if 'function' not in self._value:
                raise ValueError('`function` shoud be defined in `value`')
            if 'initial' not in self._value:
                raise ValueError('`initial` shoud be defined in `value`')
            if 'minimum' not in self._value:
                raise ValueError('`minimum` shoud be defined in `value`')
            
        if (self._state not in ['hidden', 'visible']):
            raise ValueError('`state` should be either `hidden` or `visible`')
        
        if (self._distfiles is not None) and (self._canonical_name is None):
            raise ValueError('`canonical_name` has to be defined wheen `distfiles` has value')

    def _create(self):
        self.check()

        description = self._description
        if self._author is not None:
            if description != '':
                description += '\n<br>\n\n'
            description += f'Author : {self._author}'

        connection_info = self._connection_info
        if connection_info is not None:
            connection_info = connection_info.format(server = self._server)

        try:
            id = self._ctfd.post_challenge(
                self._name, self._category, description, connection_info, 
                self._type, self._value, self._state
            )
            success(f'`{self._category}`:`{self._name}` Post Challenge Success')
        except ValueError as e:
            error(f'`{self._category}`:`{self._name}` Post Challenge Error : {e}')
            raise
        self._id = id

        if self._flag is not None:
            try:
                self._ctfd.post_challenge_flag(self._id, self._flag)
                success(f'`{self._category}`:`{self._name}` Post Flag Success')
            except ValueError as e:
                error(f'`{self._category}`:`{self._name}` Post Flag Error : {e}')
                raise

        if self._tags is not None:
            for tag in self._tags:
                try:
                    self._ctfd.post_challenge_tag(self._id, tag)
                    success(f'`{self._category}`:`{self._name}` Post Tag `{tag}` Success')
                except ValueError as e:
                    error(f'`{self._category}`:`{self._name}` Post Tag `{tag}` Error : {e}')
                    raise

        if self._distfiles is not None:
            with change_path(self._path):
                with tempfile.TemporaryDirectory() as tempdir_path:
                    zippath = os.path.join(tempdir_path, f'{self._canonical_name}.zip')
                    compress2zip(self._distfiles, zippath)
                    try:
                        self._ctfd.post_challenge_file(self._id, zippath)
                        success(f'`{self._category}`:`{self._name}` Post File `{self._canonical_name}.zip` Success')
                    except ValueError as e:
                        error(f'`{self._category}`:`{self._name}` Post File `{self._canonical_name}.zip` Error : {e}')
                        raise

        if self._hints is not None:
            for i, hint in enumerate(self._hints):
                try:
                    self._ctfd.post_challenge_hint(self._id, hint)
                    success(f'`{self._category}`:`{self._name}` Post Challenge Number {i + 1} Hint Success')
                except ValueError as e:
                    error(f'`{self._category}`:`{self._name}` Post Challenge Number {i + 1} Hint Error : {e}')
                    raise

    def post(self):
        self._create()

