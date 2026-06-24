from core.http_client import HttpClient


class BaseApi:
    def __init__(self, client: HttpClient):
        self.client = client
