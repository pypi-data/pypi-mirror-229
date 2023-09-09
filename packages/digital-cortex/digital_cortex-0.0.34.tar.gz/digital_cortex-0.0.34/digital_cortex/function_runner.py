import requests

BASE_PATH = "/api/v1/functions"


class FunctionRunner:
    def __init__(self, host_url, headers, function_id):
        self.headers = headers
        self.host_url = host_url
        self.function_id = function_id

    def execute(self, *args, **kwargs):
        payload = {"params": {"args": args, "kwargs": kwargs}}
        url = self.host_url + BASE_PATH + f'/sdk/run/{self.function_id}'
        response = requests.post(url, headers=self.headers, json=payload)
        return response.text
