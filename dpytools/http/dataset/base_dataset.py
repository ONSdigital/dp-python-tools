import json
from typing import Dict

from requests import RequestException, Response

from dpytools.http.base import BaseHttpClient
from dpytools.http.upload.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class BaseDatasetClient(BaseHttpClient):
    def __init__(self, url: str, backoff_max: int = 30):
        super().__init__(backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)
        self.url = url
        self.dataset_url = f"{self.url}/dataset"

    def send_json(self, url: str, json_data: Dict) -> None:
        """
        Send a POST request with JSON data to the specified URL.

        :param url: The URL to send the POST request to.
        :param json_data: The JSON data to include in the POST request.
        """
        try:
            response = self.post(
                url,
                headers=self.token_auth.get_auth_header(),
                json=json_data,
                verify=True,
            )
            response.raise_for_status()
            return response
        except RequestException as e:
            logger.error("Failed to send POST request", exc_info=e)
        raise

