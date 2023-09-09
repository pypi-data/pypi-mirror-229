import requests

BASE_PATH = "/api/v1/functions"


class FunctionCreator:
    def __init__(self, host_url, headers, compute_type: str, name: str, script: str, dependencies: list,
                 persistence: bool = False,
                 blocking: bool = False,
                 is_published: bool = False):
        self.function_id = None
        self.script = None
        self.headers = headers
        self.persistence = persistence
        self.host_url = host_url
        if persistence:
            url = self.host_url + BASE_PATH + '/sdk/create'
            payload = {
                "computeType": compute_type, "functionName": name, "script": script,
                "dependencies": dependencies, "async": blocking, "isPublished": is_published
            }
            response = requests.post(url, headers=self.headers, json=payload).json()
            if response.get('data') and response['data'] is not None:
                self.function_id = response['data']['id']
            else:
                raise ValueError(response)
        else:
            self.script = script
            self.payload = {
                "computeType": compute_type, "functionName": name, "script": script,
                "dependencies": dependencies, "async": blocking, "createOrUpdate": persistence,
                "isPublished": is_published
            }

    def execute(self, *args, **kwargs):
        if self.persistence:
            payload = {"params": {"args": args, "kwargs": kwargs}}
            url = self.host_url + BASE_PATH + f'/sdk/run/{self.function_id}'
            response = requests.post(url, headers=self.headers, json=payload)
            return response.text
        else:
            url = self.host_url + BASE_PATH + '/sdk/evaluate'
            params = {"params": {"args": args, "kwargs": kwargs}}
            payload = {**self.payload, **params}
            response = requests.post(url, headers=self.headers, json=payload)
            return response.text
