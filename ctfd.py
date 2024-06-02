from urllib.parse import urljoin
import requests


class CTFd:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_base_url = urljoin(base_url, '/api/v1/')

        self.api_key = api_key
        self.session = requests.session()
        self.session.headers['Authorization'] = f'Token {self.api_key}'

    def post_challenge(self, 
        name: str, 
        category: str, 
        description: str, 
        connection_info: str | None, 
        type: str, 
        value: int | dict[str, str | int], 
        state: str
    ) -> int:
        challenge_data = {
            'name': name, 
            'category': category, 
            'description': description, 
            'connection_info': connection_info, 
            'type': type, 
            'state': state
        }

        if type == 'standard':
            challenge_data['value'] = value
        elif type == 'dynamic':
            challenge_data.update(value)

        resp = self.session.post(
            urljoin(self.api_base_url, 'challenges'), 
            json = challenge_data
        )

        if resp.status_code == 200:
            return resp.json()['data']['id']
        return -1

    def post_challenge_flag(self, 
        challenge_id: int, 
        flag: str
    ) -> bool:
        resp = self.session.post(
            urljoin(self.api_base_url, 'flags'), 
            json = {
                'content': flag, 
                'data': '', 
                'type': 'static', 
                'challenge': challenge_id
            }
        )

        return resp.status_code == 200

    def post_challenge_tag(self, 
        challenge_id: int, 
        tag: str
    ) -> bool:
        resp = self.session.post(
            urljoin(self.api_base_url, 'tags'), 
            json = {
                'value': tag, 
                'challenge': challenge_id
            }
        )
    
        return resp.status_code == 200

    def post_challenge_file(self, 
        challenge_id: int, 
        filename: str
    ) -> bool:
        with open(filename, 'rb') as f:
            resp = self.session.post(
                urljoin(self.api_base_url, 'files'), 
                data = {
                    'type': 'challenge', 
                    'challenge': challenge_id
                }, 
                files = {'file': f}
            )

        return resp.status_code == 200

    def post_challenge_hint(self, 
        challenge_id: int, 
        hint: str
    ):
        resp = self.session.post(
            urljoin(self.api_base_url, 'hints'), 
            json = {
                'challenge_id': challenge_id, 
                'content': hint, 
                'cost': 0, 
                'requirements': {'prerequisites': []}
            }
        )

        return resp.status_code == 200

