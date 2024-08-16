import json
from pathlib import Path
from typing import Union

from requests.exceptions import RequestException

from dpytools.http.dataset.base_api import BaseAPIClient
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class DatasetAPIClient(BaseAPIClient):
    def __init__(self, url_netloc: str, url_path: str, backoff_max=30):
        super().__init__(url_netloc, url_path, backoff_max)

    def upload_json(self, file_path: Union[Path, str]) -> None:
        """
        Upload JSON data from the given file path.

        :param file_path: The path to the JSON file.
        """
        file_path = (
            Path(file_path).absolute() if isinstance(file_path, str) else file_path
        )

        try:
            with open(file_path, "r") as file:
                json_data = json.load(file)
            self.post_json(json_data)
        except RequestException as e:
            logger.error(f"Failed to upload JSON data: {e}", e)
            raise

    def post_new_job(self, payload=None) -> None:
        """
        Create a new job using a provided payload or a default one.

        :param payload: The payload for the new job.
        """
        if payload is None:
            payload = {
                "state": "created",
                "links": {},
                "files": [
                    {
                        "alias_name": "TestAliasName",
                        "url": "",
                    }
                ],
            }

        try:
            response = self.post_json(payload)
            if response.status_code != 201:
                logger.error(
                    f"Job not created, returning status code: {response.status_code}"
                )
                raise Exception(
                    f"Job not created, returning status code: {response.status_code}"
                )
            logger.info("Job created successfully")
        except RequestException as e:
            logger.error(f"Failed to create a new job: {e}")
            raise
