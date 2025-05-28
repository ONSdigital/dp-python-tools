from dpytools.http.api.models.dataset import GetDatasetResponse
from dpytools.http.base_http import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger
from dpytools.http.api.base_dataset_api_client import BaseDatasetAPIClient


class DatasetsService(BaseDatasetAPIClient):
    def __init__(
        self,
        dataset_api_url: str,
        logger: DpLogger,
        http_client: BaseHttpClient,
        token_auth: TokenAuth,
    ):
        super().__init__(dataset_api_url, logger, http_client, token_auth)

    def _build_full_url(self, dataset_id: str) -> str:
        return f"{self._dataset_api_url}/{dataset_id}"

    def get_dataset(self, dataset_id: str) -> GetDatasetResponse:
        request_method = "GET"
        url = self._build_full_url(dataset_id)

        response = self._http_client.get(
            url=url,
            headers=self._get_request_headers(),
            verify=True,
        )

        response = self._handle_response(
            response=response, request_method=request_method, url=url
        )

        json = response.json()

        return GetDatasetResponse(**json)
