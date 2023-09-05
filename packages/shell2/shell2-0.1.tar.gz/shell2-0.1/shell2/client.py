import requests
import os
import time
import random

N_TRIALS = 1
EXP_BACKOFF_MS = 1000

class Shell2Client:

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = SessionAPI(self)
        self.sequence = SequenceAPI(self)
        self.settings = SettingsAPI(self)
        self.storage = StorageAPI(self)

    def _api_post(self, route, body={}):
        current_trial = 0
        while current_trial < N_TRIALS:
            current_trial += 1
            try:
                response = requests.post(
                    f'https://api.shell2.raiden.ai/{route}',
                    json=body,
                    headers={
                        'Content-Type': 'application/json',
                        'key': self.api_key,
                    }
                )
                return response.json()
            except requests.exceptions.RequestException as error:
                if error.response.status_code == 429:
                    delay_ms = (EXP_BACKOFF_MS * 2 ** current_trial) + random.randint(1000, 2000)
                    time.sleep(delay_ms / 1000.0)
                else:
                    return False
        return False

class SessionAPI:

    def __init__(self, client):
        self.client = client

    def new(self, query):
        return self.client._api_post('session/new', query)

    def update(self, query):
        return self.client._api_post('session/update', query)

    def resume(self, query):
        return self.client._api_post('session/resume', query)

    def message(self, query):
        return self.client._api_post('session/message', query)

    def list(self):
        return self.client._api_post('session/list', {})

    def get(self, query):
        return self.client._api_post('session/get', query)

class SequenceAPI:

    def __init__(self, client):
        self.client = client

    def run(self, query):
        return self.client._api_post('sequence/run', query)

    def update(self, query):
        return self.client._api_post('sequence/update', query)

    def list(self):
        return self.client._api_post('sequence/list', {})

    def get(self, query):
        return self.client._api_post('sequence/get', query)

class SettingsAPI:

    def __init__(self, client):
        self.client = client

    def get(self):
        return self.client._api_post('user/settings/get', {})

    def update(self, query):
        return self.client._api_post('user/settings/update', query)

    def reset(self, query):
        return self.client._api_post('user/settings/update', {'reset': True})

class StorageAPI:

    def __init__(self, client):
        self.client = client

    def upload(self, query):
        filename = os.path.basename(query.get('filename', query.get('filepath', '')))
        if filename == '.':
            return {'status': False, 'error': 'invalid file'}

        sign_response = self.client._api_post('user/storage/upload', {'filename': filename})
        url = sign_response['url']
        mime = sign_response['mime']
        headers = {'Content-Type': mime} if mime else {}

        try:
            with open(query['filepath'], 'rb') as file:
                response = requests.put(url, data=file.read(), headers=headers)
                return {'status': True, 'filepath': query['filepath'], 'filename': filename, 'mime': mime}
        except Exception as e:
            return {'status': False, 'error': str(e)}

    def download(self, query):
        try:
            return self.client._api_post('user/storage/download', query)
            """
            download_response = self.client._api_post('user/storage/download', query)
            url = download_response['url']

            if 'output' not in query:
                return {'status': True, 'url': url}

            response = requests.get(url)
            with open(query['output'], 'wb') as file:
                file.write(response.content)
            return {'status': True, 'url': url, 'filename': query['filename'], 'output': query['output']}
            """
        except Exception as e:
            return {'status': False, 'error': str(e)}
