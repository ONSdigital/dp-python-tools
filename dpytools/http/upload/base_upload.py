from abc import abstractmethod
from pathlib import Path
from typing import Union

from requests import Response

from dpytools.http.base_http import BaseHttpClient
from dpytools.logging.logger import DpLogger

from ..token_auth import TokenAuth

logger = DpLogger("dpytools")


class BaseUploadClient(BaseHttpClient):
    def __init__(self, upload_url: str, backoff_max=30):
        super().__init__(backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)
        self.upload_url = upload_url

    @abstractmethod
    def upload(self, file_path: Union[Path, str], mimetype: str) -> Response:
        pass
