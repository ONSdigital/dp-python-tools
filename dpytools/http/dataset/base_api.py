from typing import Dict

from requests import RequestException, Response

from dpytools.http.base import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class BaseAPIClient(BaseHttpClient):
    def __init__(self, url_netloc: str, url_path: str, backoff_max: int = 30):
        super().__init__(backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)
        self.url_netloc = url_netloc
        self.url_path = url_path

    def build_full_url(self) -> str:
        """
        Build the full URL from the netloc and path.

        :return: The full URL.
        """
        return f"http://{self.url_netloc.rstrip('/')}/{self.url_path.lstrip('/')}"

    def post_json(self, json_data: Dict) -> Response:
        """
        Send a POST request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the POST request.
        :return: The response from the POST request.
        """
        full_url = self.build_full_url()
        try:
            response = self.post(
                full_url,
                headers=self.token_auth.get_auth_header(),
                json=json_data,
                verify=True,
            )
            return response
        except RequestException as e:
            logger.error("Failed to send POST request", exc_info=e)
            raise
