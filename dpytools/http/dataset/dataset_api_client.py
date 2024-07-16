# dataset_api_client.py

import json
from pathlib import Path
from typing import Dict, Union

from requests.exceptions import RequestException

from dpytools.http.dataset.base_dataset import BaseDatasetClient
from dpytools.http.upload.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class DatasetAPIClient(BaseDatasetClient):
    def __init__(self, url: str, upload_dict: Dict, backoff_max=30):
        super().__init__(url, backoff_max)
        self._assign(upload_dict)

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
        Job is created in the state 'created'.
        """
        for dataset_id, data in self.upload_dict.items():
            s3_url = data.get("s3_url")
            if not s3_url:
                raise ValueError(
                    f"Aborting. s3_url is required for {dataset_id}, can be added manually."
                )

            self._get_recipe_id(dataset_id)

            payload = {
                "recipe": data["recipe_id"],
                "state": "created",
                "links": {},
                "files": [
                    {
                        "alias_name": data["dataset_recipe"]["files"][0]["description"],
                        "url": s3_url,
                    }
                ],
            }

            response = self.post(
                f"{self.dataset_url}/jobs",
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
