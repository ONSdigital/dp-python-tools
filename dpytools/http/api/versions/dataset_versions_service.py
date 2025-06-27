from typing import Dict, Union

from requests import Response
from dpytools.http.api.models.common import DatasetState
from dpytools.http.api.models.version import GetDatasetVersionsResponse
from dpytools.http.base_http import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger
from dpytools.http.api.base_dataset_api_client import BaseDatasetAPIClient


class DatasetVersionsService(BaseDatasetAPIClient):
    def __init__(
        self,
        dataset_api_url: str,
        logger: DpLogger,
        http_client: BaseHttpClient,
        token_auth: TokenAuth,
    ):
        super().__init__(dataset_api_url, logger, http_client, token_auth)

    def _build_full_url(self, dataset_id: str, edition_id: str) -> str:
        return f"{self._dataset_api_url}/{dataset_id}/editions/{edition_id}/versions"

    def get_versions(
        self, dataset_id: str, edition_id: str, params: Union[Dict, None] = None
    ) -> GetDatasetVersionsResponse:
        """
        Send a GET request to the specified URL.
        :param  params: The params to include in the GET request.
        :return: The response from the GET request.
        """
        request_method = "GET"
        url = self._build_full_url(dataset_id, edition_id)
        self._log_request(request_method=request_method, url=url)
        response = self._http_client.get(
            url,
            params=params,
            headers=self._get_request_headers(),
            verify=True,
        )

        response = self._handle_response(
            response=response, request_method=request_method, url=url
        )

        json = response.json()
        return GetDatasetVersionsResponse(**json)

    def create_version(
        self, json_data: Dict, dataset_id: str, edition_id: str
    ) -> Response:
        """
        Send a POST request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the POST request.
        :return: The response from the POST request.
        """
        request_method = "POST"
        url = self._build_full_url(dataset_id, edition_id)
        self._log_request(request_method=request_method, body=json_data, url=url)
        response = self._http_client.post(
            url,
            headers=self._get_request_headers(),
            json=json_data,
            verify=True,
        )

        return self._handle_response(
            response=response, request_method=request_method, body=json_data, url=url
        )

    def update_version(
        self, json_data: Dict, dataset_id: str, edition_id: str
    ) -> Response:
        """
        Send a PUT request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the PUT request.
        :return: The response from the PUT request.
        """
        request_method = "PUT"
        url = self._build_full_url(dataset_id, edition_id)
        self._log_request(request_method=request_method, body=json_data, url=url)

        response = self._http_client.put(
            url,
            headers=self._get_request_headers(),
            json=json_data,
            verify=True,
        )

        return self._handle_response(
            response=response, request_method=request_method, body=json_data, url=url
        )

    def update_version_state(
        self, dataset_id: str, edition_id: str, version: int | str, state: DatasetState
    ) -> Response:
        """
        Update a version's state
        """
        request_method = "PUT"
        url = self._build_full_url(dataset_id, edition_id) + f"/{version}/state"
        json_data = {"state": state}
        self._log_request(request_method=request_method, body=json_data, url=url)

        response = self._http_client.put(
            url,
            headers=self._get_request_headers(),
            json=json_data,
            verify=True,
        )

        return self._handle_response(
            response=response, request_method=request_method, body=json_data, url=url
        )
