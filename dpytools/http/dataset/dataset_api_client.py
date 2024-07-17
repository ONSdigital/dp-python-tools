import json
from pathlib import Path
from typing import Union

from requests.exceptions import RequestException

from dpytools.http.dataset.base_dataset import BaseDatasetClient
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class DatasetAPIClient(BaseDatasetClient):
    def __init__(self, url: str, backoff_max=30):
        super().__init__(url, backoff_max)

    def upload_json(self, file_path: Union[Path, str]) -> None:
        """
        Upload JSON data from the given file path.

        :param file_path: The path to the JSON file.
        """
        file_path = (
            Path(file_path).absolute() if isinstance(file_path, str) else file_path
        )

        with open(file_path, "r") as file:
            json_data = json.load(file)

        try:
            self.send_json(self.url, json_data)
        except RequestException as e:
            logger.error(f"Failed to upload JSON data: {e}")
            raise

    def post_new_job(self) -> None:
        """
        Creates a new job in the /dataset/jobs API.
        """
        payload = {
            "recipe": "hardcoded_recipe_id",
            "state": "created",
            "links": {},
            "files": [
                {
                    "alias_name": "TestAliasName",
                    "url": "",
                }
            ],
        }

        # Hardcoded URL for demonstration purposes
        hardcoded_url = "http://example.com/dataset/jobs"

        response = self.post(
            hardcoded_url,
            headers={
                "X-Florence-Token": self.token_auth.auth_token,
                "ID": self.token_auth.id_token,
            },
            json=payload,
            verify=True,
        )
        if response.status_code == 201:
            logger.info("Job created successfully")
        else:
            raise Exception(
                f"Job not created, returning status code: {response.status_code}"
            )
