import os
import requests
from urllib.parse import urljoin

from dotenv import load_dotenv


class CTFd:
    def __init__(self, 
        env_path: str | None = None, 
        base_url: str | None = None, 
        token: str | None = None, 
        server: str | None = None
    ):
        if (env_path is None) and ((base_url is None) or (token is None) or (server is None)):
            raise ValueError('`env_path` or (`base_url` and `token` and `server`) has to be specify')

        if (env_path is not None):
            self._load_settings(env_path)
        else:
            self._base_url = base_url
            self._token = token
            self._server = server

        self._api_base_url = urljoin(self._base_url, '/api/v1/')
        self._session = requests.session()
        self._session.headers['Authorization'] = f'Token {self._token}'

    def _load_settings(self, env_path: str):
        load_dotenv(env_path)
        if ('BASE_URL' not in os.environ) or ('TOKEN' not in os.environ) or ('SERVER' not in os.environ):
            raise ValueError(f'need to set `BASE_URL`, `TOKEN` and `SERVER` in {env_path}')

        self._base_url = os.getenv('BASE_URL')
        self._token = os.getenv('TOKEN')
        self._server = os.getenv('SERVER')

    def _post(self, 
        api_path: str, 
        json: dict | None = None, 
        data: dict | None = None, 
        files: dict | None = None
    ):
        return self._session.post(
            urljoin(self._api_base_url, api_path), 
            json = json, 
            data = data, 
            files = files
        )

    def _check_status_code(self, status_code: int):
        if status_code != 200:
            raise ValueError(f'HTTP request failed. Status Code : {status_code}')

    def post_challenge(self, 
        name: str, 
        category: str, 
        description: str, 
        connection_info: str | None, 
        type: str, 
        value: int | dict[str, str | int], 
        state: str
    ) -> int:
        post_data = {
            'name': name, 
            'category': category, 
            'description': description, 
            'connection_info': connection_info, 
            'type': type, 
            'state': state
        }

        if type == 'standard':
            post_data['value'] = value
        elif type == 'dynamic':
            post_data.update(value)

        response = self._post(
            'challenges', 
            json = post_data
        )

        self._check_status_code(response.status_code)
        return response.json()['data']['id']

    def post_challenge_flag(self, 
        challenge_id: int, 
        flag: str
    ):
        response = self._post(
            'flags', 
            json = {
                'content': flag, 
                'data': '', 
                'type': 'static', 
                'challenge': challenge_id
            }
        )
        self._check_status_code(response.status_code)

    def post_challenge_tag(self, 
        challenge_id: int, 
        tag: str
    ):
        response = self._post(
            'tags', 
            json = {
                'value': tag, 
                'challenge': challenge_id
            }
        )
        self._check_status_code(response.status_code)

    def post_challenge_file(self, 
        challenge_id: int, 
        filepath: str
    ):
        with open(filepath, 'rb') as f:
            response = self._post(
                'files', 
                data = {
                    'type': 'challenge', 
                    'challenge': challenge_id
                }, 
                files = { 'file': f }
            )
            self._check_status_code(response.status_code)

    def post_challenge_hint(self, 
        challenge_id: int, 
        hint: str
    ):
        response = self._post(
            'hints', 
            json = {
                'challenge_id': challenge_id, 
                'content': hint, 
                'cost': 0, 
                'requirements': { 'prerequisites': [] }
            }
        )
        self._check_status_code(response.status_code)

