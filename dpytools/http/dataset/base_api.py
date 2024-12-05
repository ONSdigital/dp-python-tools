from typing import Dict

from dpytools.http.base import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger
from abc import ABC, abstractmethod

logger = DpLogger("dpytools")

class BaseAPIClient(BaseHttpClient, ABC):
    def __init__(self, url_netloc: str, url_path: str, backoff_max: int = 30):
        super().__init__(backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)
        self.url_netloc = url_netloc
        self.url_path = url_path
        self.full_url = f"{url_netloc.rstrip('/')}/{url_path.lstrip('/')}"

    @abstractmethod
    def post_json(self, json_data: Dict):
        """Send a POST request with JSON data."""
        pass

    @abstractmethod
    def put_json(self, json_data: Dict):
        """Send a PUT request with JSON data."""
        pass