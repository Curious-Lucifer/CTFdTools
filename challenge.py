import os
import re
import tempfile
import yaml

from pydantic import BaseModel, field_validator

from .ctfd import CTFd
from .utils import change_path, check_canonical, compress2zip


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
        challenge_path: str = '.', 
        ctfd: CTFd | None = None, 
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
        self.challenge_path = challenge_path
        self.ctfd = ctfd

        self.name = name
        self.category = category
        self.description = description
        self.author = author
        self.connection_info = connection_info
        self.flag = flag
        self.tags = tags
        self.distfiles = distfiles
        self.hints = hints

        self.type = type
        self.value = value
        self.state = state

        self.canonical_name = canonical_name

        self.challenge_id = None

    def load_yaml(self, filename: str = 'task.yaml'):
        with open(os.path.join(self.challenge_path, filename)) as f:
            y = yaml.safe_load(f)
        challenge_from_yaml = ChallengeYamlModel(**y)

        self.name = challenge_from_yaml.name if challenge_from_yaml.name is not None else self.name
        self.category = challenge_from_yaml.category if challenge_from_yaml.category is not None else self.category
        self.description = challenge_from_yaml.description if challenge_from_yaml.description is not None else self.description
        self.author = challenge_from_yaml.author if challenge_from_yaml.author is not None else self.author
        self.connection_info = challenge_from_yaml.connection_info if challenge_from_yaml.connection_info is not None else self.connection_info
        self.flag = challenge_from_yaml.flag if challenge_from_yaml.flag is not None else self.flag
        self.tags = challenge_from_yaml.tags if challenge_from_yaml.tags is not None else self.tags
        self.distfiles = challenge_from_yaml.distfiles if challenge_from_yaml.distfiles is not None else self.distfiles
        self.hints = challenge_from_yaml.hints if challenge_from_yaml.hints is not None else self.hints

        self.type = challenge_from_yaml.type if challenge_from_yaml.type is not None else self.type
        self.value = challenge_from_yaml.value if challenge_from_yaml.value is not None else self.value
        self.state = challenge_from_yaml.state if challenge_from_yaml.state is not None else self.state

        self.canonical_name = challenge_from_yaml.canonical_name if challenge_from_yaml.canonical_name is not None else self.canonical_name

    def check(self) -> bool:
        if self.ctfd is None:
            return False

        if (self.name is None) or (self.category is None):
            return False

        if self.type not in ['standard', 'dynamic']:
            return False
        
        if self.type == 'dynamic':
            if ('function' not in self.value) or ('initial' not in self.value) or ('minimum' not in self.value):
                return False

        if self.state not in ['hidden', 'visible']:
            return False

        if self.canonical_name is None:
            return False
        if not check_canonical(self.canonical_name):
            return False

        return True

    def create(self):
        if not self.check():
            assert False, 'Object Uninitialize'

        description = self.description
        if self.author is not None:
            if self.description != '':
                description += '\n<br>\n\n'
            description += f'Author : {self.author}'

        challenge_id = self.ctfd.post_challenge(
            self.name, self.category, description, self.connection_info, 
            self.type, self.value, self.state
        )
        if challenge_id == -1:
            assert False, f'Create Challenge Error : {self.category}:{self.name}'
        self.challenge_id = challenge_id

        if self.flag is not None:
            if not self.ctfd.post_challenge_flag(self.challenge_id, self.flag):
                assert False, f'Post Flag Error : {self.category}:{self.name} - {self.flag}'

        if self.tags is not None:
            for tag in self.tags:
                if not self.ctfd.post_challenge_tag(self.challenge_id, tag):
                    assert False, f'Post Tag Error : {self.category}:{self.name} - {tag}'

        if self.distfiles is not None:
            with change_path(self.challenge_path):
                with tempfile.TemporaryDirectory() as tempdir_path:
                    zippath = os.path.join(tempdir_path, f'{self.canonical_name}.zip')
                    compress2zip(self.distfiles, zippath)
                    if not self.ctfd.post_challenge_file(self.challenge_id, zippath):
                        assert False, f'Post File Error : {self.category}:{self.name}'

        if self.hints is not None:
            for hint in self.hints:
                if not self.ctfd.post_challenge_hint(self.challenge_id, hint):
                    assert False, f'Post Hint Error : {self.category}:{self.name} - {hint}'


