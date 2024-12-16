from typing import Dict

from requests import Response

from dpytools.http.dataset.base_api import BaseAPIClient
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class DatasetAPIClient(BaseAPIClient):
    def __init__(self, url_netloc: str, url_path: str, backoff_max=30):
        super().__init__(url_netloc, url_path, backoff_max)

    def post_json(self, json_data: Dict) -> Response:
        """
        Send a POST request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the POST request.
        :return: The response from the POST request.
        """
        response = self.post(
            self.full_url,
            headers=self.token_auth.get_auth_header(),
            json=json_data,
            verify=True,
        )
        if response.status_code != 201:
            raise Exception(
                f"POST request failed with status code: {response.status_code}"
            )
        return response

    def put_json(self, json_data: Dict) -> Response:
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
