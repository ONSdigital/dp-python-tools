from dpytools.http.base_http import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger
from dpytools.http.api.versions.dataset_versions_service import DatasetVersionsService
from dpytools.http.api.datasets.datasets_service import DatasetsService


class DatasetAPIService:
    def __init__(self, dataset_api_url: str):
        self._logger = DpLogger("DatasetAPIClient")
        self._http_client = BaseHttpClient()
        self._token_auth = TokenAuth()
        self.dataset_api_url = dataset_api_url.strip("/")
        self.versions = DatasetVersionsService(
            self.dataset_api_url, self._logger, self._http_client, self._token_auth
        )
        self.datasets = DatasetsService(
            self.dataset_api_url, self._logger, self._http_client, self._token_auth
        )
