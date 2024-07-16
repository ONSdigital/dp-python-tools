import json
from typing import Dict

from requests import RequestException, Response

from dpytools.http.base import BaseHttpClient
from dpytools.http.upload.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")


class BaseDatasetClient(BaseHttpClient):
    def __init__(self, url: str, backoff_max: int = 30):
        super().__init__(backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)
        self.url = url
        self.dataset_url = f"{self.url}/dataset"

    def send_json(self, url: str, json_data: Dict) -> None:
        """
        Send a POST request with JSON data to the specified URL.

        :param url: The URL to send the POST request to.
        :param json_data: The JSON data to include in the POST request.
        """
        try:
            response = self.post(
                url,
                headers=self.token_auth.get_auth_header(),
                json=json_data,
                verify=True,
            )
            response.raise_for_status()
            return response
        except RequestException as e:
            logger.error("Failed to send POST request", exc_info=e)
        raise

    def _assign(self, upload_dict: Dict) -> None:
        """
        Assign the upload dictionary to the instance variable.

        :param upload_dict: Dictionary containing upload data.
        """
        if not hasattr(self, "upload_dict"):
            self.upload_dict = upload_dict
        else:
            logger.warning("upload_dict is already assigned.")

    def _get_recipe_id(self, dataset_id: str) -> None:
        """
        Get the recipe ID for the given dataset ID if not already set.

        :param dataset_id: The ID of the dataset to get the recipe for.
        """
        if not self.upload_dict[dataset_id].get("recipe_id"):
            response = self.get(f"{self.dataset_url}/recipes?limit=1000")

            if response.status_code == 200:
                all_recipes = response.json()
            else:
                raise Exception(f"Recipe API returned a {response.status_code} error")

            for item in all_recipes["items"]:
                if dataset_id == item["output_instances"][0]["dataset_id"]:
                    self.upload_dict[dataset_id]["dataset_recipe"] = item
                    self.upload_dict[dataset_id]["recipe_id"] = item["id"]
                    return

            raise Exception(f"Unable to find recipe for dataset id {dataset_id}")
