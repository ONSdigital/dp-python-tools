from typing import Dict, Optional, Union

from requests import Response
from requests.exceptions import HTTPError

from dpytools.http.base_http import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class DatasetAPIClient(BaseHttpClient):
    def __init__(self, dataset_api_url: str, dataset_path: str, edition_path: str):
        self.token_auth = TokenAuth()
        self.dataset_api_url = dataset_api_url.strip("/")
        self.dataset_path = dataset_path.strip("/")
        self.edition_path = edition_path.strip("/")
        self.full_url = (
            f"{dataset_api_url}/{dataset_path}/editions/{edition_path}/versions"
        )

    # When writing to the metadata api we want to first determine whether our dataset id already exists. If it does not we will receive a 404 error.
    # In which case we do NOT want to retry the API request
    def get_path(self, params: Union[Dict, None] = None) -> Response:
        """
        Send a GET request to the specified URL.
        :param  params: The params to include in the GET request.
        :return: The response from the GET request.
        """
        request_method = "GET"
        self._log_request(request_method=request_method)
        response = self.get(
            self.full_url,
            params=params,
            headers=self.token_auth.get_auth_header(),
            verify=True,
        )

        return self._handle_response(response=response, request_method=request_method)

    def post_json(self, json_data: Dict) -> Response:
        """
        Send a POST request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the POST request.
        :return: The response from the POST request.
        """
        request_method = "POST"
        self._log_request(request_method=request_method, body=json_data)
        response = self.post(
            self.full_url,
            headers=self.token_auth.get_auth_header(),
            json=json_data,
            verify=True,
        )

        return self._handle_response(
            response=response, request_method=request_method, body=json_data
        )

    def put_json(self, json_data: Dict) -> Response:
        """
        Send a PUT request with JSON data to the specified URL.

        :param json_data: The JSON data to include in the PUT request.
        :return: The response from the PUT request.
        """
        request_method = "PUT"
        self._log_request(request_method=request_method, body=json_data)

        response = self.put(
            self.full_url,
            headers=self.token_auth.get_auth_header(),
            json=json_data,
            verify=True,
        )

        return self._handle_response(
            response=response, request_method=request_method, body=json_data
        )

    def _handle_response(
        self, response: Response, request_method: str, body: Optional[Dict] = None
    ) -> Response:
        data = self._get_log_data(
            request_method=request_method, body=body, response=response.content
        )
        try:
            logger.debug(
                f"Received response code {response.status_code}",
                data=data,
                response=response,
            )
            response.raise_for_status()
            return response
        except HTTPError as err:
            logger.error(
                f"{request_method} failed", data=data, error=err, response=response
            )
            raise Exception(
                f"{request_method} failed with status code: {response.status_code}"
            ) from err

    def _log_request(self, request_method: str, body: Optional[Dict] = None):
        data = self._get_log_data(request_method=request_method, body=body)
        logger.debug(f"Sending {request_method} request", data=data)

    def _get_log_data(
        self,
        request_method: str,
        response: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> dict:
        data = {"method": request_method, "url": self.full_url}

        if response is not None:
            data["response"] = response

        if body is not None:
            data["json"] = body

        return data
