import datetime
from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from dpytools.http.api.datasets.datasets_service import DatasetsService
from dpytools.http.api.models.dataset import DatasetType

@pytest.fixture
def datasets_service():
    logger = MagicMock()
    http_client = MagicMock()
    token_auth = MagicMock()
    mock_service = DatasetsService(
        "http://test_url", logger, http_client, token_auth
    )
    
    return mock_service

def raise_for_status(mock_response: Response):
    if mock_response.status_code < 200 or mock_response.status_code > 299:
        raise Exception("Error")

def test_get_dataset_success(datasets_service: DatasetsService):
    dataset_id = "test_dataset_path"
    url = f"http://test_url/{dataset_id}"
    mock_response = MagicMock(Response)
    mock_response.status_code = 201
    mock_response.url = url
    mock_response.headers = {
        "Date": str(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
    }
    mock_response.json.return_value = {
        "id": "test_dataset_path",
        "current": {"state": "created", "type": "static"},
        "next": {"state": "completed", "title": "example", "type": "static"},
    }

    mock_response.elapsed = datetime.timedelta(seconds=1)

    mock_response_request_mock = MagicMock()
    mock_response.request = mock_response_request_mock
    mock_response_request_mock.method = "GET"
    datasets_service._http_client.get.return_value = mock_response

    dataset = datasets_service.get_dataset(dataset_id)

    assert dataset.id == "test_dataset_path"
    assert dataset.current and dataset.current.type == DatasetType.STATIC
    assert dataset.next and dataset.next.title == "example"

    assert not dataset.can_publish_new_version()