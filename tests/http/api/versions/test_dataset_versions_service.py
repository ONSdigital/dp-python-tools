import datetime
from unittest.mock import MagicMock

import pytest
from requests import Response

from dpytools.http.api.versions.dataset_versions_service import DatasetVersionsService
from dpytools.logging.response_error import DatasetResponseError


@pytest.fixture
def dataset_versions_service():
    logger = MagicMock()
    http_client = MagicMock()
    token_auth = MagicMock()
    mock_service = DatasetVersionsService(
        "http://test_url", logger, http_client, token_auth
    )

    return mock_service


def raise_for_status(mock_response: Response):
    if mock_response.status_code < 200 or mock_response.status_code > 299:
        raise Exception("Error")


def test_create_version_success(dataset_versions_service: DatasetVersionsService):
    """
    Test that the post_json method sends the correct payload to the correct URL
    """
    # Mock the token authentication response

    url = "http://test_url/test_dataset_path/editions/test_edition_path/versions"
    mock_response = MagicMock(Response)
    mock_response.status_code = 201
    mock_response.content = b"Test response content"
    mock_response.url = url
    mock_response.headers = {
        "Date": str(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
    }
    mock_response.elapsed = datetime.timedelta(seconds=1)

    mock_response_request_mock = MagicMock()
    mock_response.request = mock_response_request_mock
    mock_response_request_mock.method = "POST"

    dataset_versions_service._http_client.post.return_value = mock_response

    mock_client = dataset_versions_service

    dataset_id = "test_dataset_path"
    edition_id = "test_edition_path"
    response = mock_client.create_version(
        {"key": "value"}, dataset_id=dataset_id, edition_id=edition_id
    )

    assert response.status_code == 201
    # Verify response content
    assert response.content.decode() == "Test response content"
    dataset_versions_service._http_client.post.assert_called_with(
        f"http://test_url/{dataset_id}/editions/{edition_id}/versions",
        headers=mock_client._token_auth.get_auth_header(),
        json={"key": "value"},
        verify=True,
    )


def test_create_version_failure(dataset_versions_service: DatasetVersionsService):
    """
    Test that the post_json method raises an exception when the response status code is not 201
    """
    # Setup mock responses to simulate failure
    mock_response = MagicMock(Response)
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = lambda: raise_for_status(mock_response)
    dataset_versions_service._http_client.post.return_value = mock_response

    mock_client = dataset_versions_service
    dataset_id = "test_dataset_path"
    edition_id = "test_edition_path"

    with pytest.raises(Exception):
        mock_client.create_version({"key": "value"}, dataset_id, edition_id)


def test_update_version_success(dataset_versions_service: DatasetVersionsService):
    """
    Test that the put_json method sends the correct payload to the correct URL
    """
    url = "http://test_url/test_dataset_path/editions/test_edition_path/versions"

    # Mock the token authentication response
    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.content = b"Test response content"
    dataset_versions_service._http_client.put.return_value = mock_response
    mock_response.url = url
    mock_response.headers = {
        "Date": str(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
    }
    mock_response.elapsed = datetime.timedelta(seconds=1)

    mock_response_request_mock = MagicMock()
    mock_response.request = mock_response_request_mock
    mock_response_request_mock.method = "PUT"
    dataset_id = "test_dataset_path"
    edition_id = "test_edition_path"

    mock_client = dataset_versions_service
    response = mock_client.update_version({"key": "value"}, dataset_id, edition_id)

    assert response.status_code == 200
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_client._http_client.put.assert_called_with(
        url,
        headers=mock_client._token_auth.get_auth_header(),
        json={"key": "value"},
        verify=True,
    )


def test_update_version_failure(dataset_versions_service: DatasetVersionsService):
    """
    Test that the put_json method raises an exception when the response status code is not 200
    """
    # Mock the token authentication response

    # Setup mock responses to simulate failure
    mock_response = MagicMock(Response)
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = lambda: raise_for_status(mock_response)

    dataset_versions_service._http_client.put.return_value = mock_response

    mock_client = dataset_versions_service
    dataset_id = "test_dataset_path"
    edition_id = "test_edition_path"

    with pytest.raises(Exception):
        mock_client.update_version({"key": "value"}, dataset_id, edition_id)


def test_get_versions_success(dataset_versions_service: DatasetVersionsService):
    url = "http://test_url/test_dataset_path/editions/test_edition_path/versions"

    mock_response = MagicMock(Response)
    mock_response.status_code = 200

    mock_versions = {
        "items": [
            {
                "edition_title": "edition",
                "distributions": [],
                "release_date": datetime.datetime.now().isoformat(),
                "state": "completed",
                "version": 1,
            }
        ]
    }

    mock_response.json.side_effect = lambda: mock_versions
    dataset_versions_service._http_client.get.return_value = mock_response
    mock_response.url = url
    mock_response.headers = {
        "Date": str(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
    }
    mock_response.elapsed = datetime.timedelta(seconds=1)
    mock_response_request_mock = MagicMock()
    mock_response.request = mock_response_request_mock
    mock_response_request_mock.method = "GET"
    dataset_id = "test_dataset_path"
    edition_id = "test_edition_path"

    mock_client = dataset_versions_service
    response = mock_client.get_versions(dataset_id, edition_id, params={"key": "value"})
    assert len(response.items) == 1
    assert response.items[0].edition_title == "edition"

    dataset_versions_service._http_client.get.assert_called_with(
        url,
        headers=mock_client._token_auth.get_auth_header(),
        params={"key": "value"},
        verify=True,
    )


def test_map_error_json_to_object():
    """
    Tests that an input error dictionary matching the expected structure
    is successfully mapped to a DatasetResponseError object.
    """
    error_dict = {
        "Cause": "Error cause",
        "Code": "TestErrorCode",
        "Description": "Error description",
    }

    test_cause = error_dict["Cause"]
    test_code = error_dict["Code"]
    test_description = error_dict["Description"]

    test_error_response = DatasetResponseError(
        cause=test_cause, error_code=test_code, description=test_description
    )

    assert test_error_response
    assert test_error_response.cause == "Error cause"
    assert test_error_response.error_code == "TestErrorCode"
    assert test_error_response.description == "Error description"
