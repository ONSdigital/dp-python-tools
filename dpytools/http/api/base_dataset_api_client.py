from dpytools.http.base_http import BaseHttpClient
from typing import Dict, Optional

from requests import Response
from requests.exceptions import HTTPError

from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger


class BaseDatasetAPIClient:
    def __init__(
        self,
        dataset_api_url: str,
        logger: DpLogger,
        http_client: BaseHttpClient,
        token_auth: TokenAuth,
    ):
        self._dataset_api_url = dataset_api_url
        self._logger = logger
        self._http_client = http_client
        self._token_auth = token_auth

    def _get_request_headers(self) -> Dict[str, str]:
        return self._token_auth.get_auth_header()

    def _handle_response(
        self,
        response: Response,
        request_method: str,
        url: str,
        body: Optional[Dict] = None,
    ) -> Response:
        """
        Log response and raise exception for Response status if appropriate.
        """
        data = self._get_log_data(
            request_method=request_method,
            url=url,
            body=body,
            response=str(response.content),
        )
        try:
            self._logger.debug(
                f"Received response code {response.status_code}",
                data=data,
                response=response,
            )
            response.raise_for_status()
            return response
        except HTTPError as err:
            self._logger.error(
                f"{request_method} failed", data=data, error=err, response=response
            )
            raise Exception(
                f"{request_method} failed with status code: {response.status_code}"
            ) from err

    def _log_request(self, request_method: str, url: str, body: Optional[Dict] = None):
        """
        Log request data
        """
        data = self._get_log_data(request_method=request_method, url=url, body=body)
        self._logger.debug(f"Sending {request_method} request", data=data)

    def _get_log_data(
        self,
        request_method: str,
        url: str,
        response: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> dict:
        data: Dict[str, str | dict] = {"method": request_method, "url": url}

        if response is not None:
            data["response"] = response

        if body is not None:
            data["json"] = body

        return data
