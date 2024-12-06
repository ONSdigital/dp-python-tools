from abc import ABC, abstractmethod
from email import header
from enum import verify
from typing import Dict
from urllib import response
from urllib.request import Request

from dpytools.http.base import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger

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
        """
        Send a POST request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the POST request.
        :return: The response from the POST request.
        """
        response = self.post(
            self.full_url,
            headers=self.token_auth.get_auth_header(),
            json=json_data,
            verify=True
        )
        if response.status_code != 201:
            raise Exception(
                f"POST request failed with status code: {response.status_code}"
            )
        return response

    @abstractmethod
    def put_json(self, json_data: Dict):
        """
        Send a PUT request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the PUT request.
        :return: The response from the PUT request.
        """
        response = self.put(
            self.full_url,
            headers=self.token_auth.get_auth_header(),
            json=json_data,
            verify=True,
        )
        if response.status_code != 200:
            raise Exception(
                f"PUT request failed with status code: {response.status_code}"
            )
        return response
