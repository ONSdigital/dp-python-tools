from typing import Dict, Union

import backoff
from requests import Response
from requests.exceptions import HTTPError

from dpytools.http.base import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class DatasetAPIClient(BaseHttpClient):
    def __init__(self, url_netloc: str, url_path: str, backoff_max: int = 30):
        super().__init__(backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)
        self.url_netloc = url_netloc
        self.url_path = url_path
        self.full_url = f"{url_netloc.rstrip('/')}/{url_path.lstrip('/')}"

    # When writing to the metadata api we want to first determine whether our dataset id already exists. If it does not we will receive a 404 error.
    # In which case we do NOT want to retry the API request
    @backoff.on_exception(backoff.expo, HTTPError, max_time=30, giveup=lambda e: True)
    def get_path(self, params: Union[Dict, None] = None) -> Response:
        """
        Send a GET request to the specified URL.

        :param  params: The params to include in the GET request.
        :return: The response from the GET request.
        """

        response = self.get(
            self.full_url,
            params=params,
            headers=self.token_auth.get_auth_header(),
            verify=True,
        )

        return response

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
