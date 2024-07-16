import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from requests import HTTPError, RequestException, Response

from dpytools.http.dataset.dataset_api_client import DatasetAPIClient


def client():
    """
    Create a DatasetAPIClient instance for testing
    """
    url = "http://test_url"
    upload_dict = {
        "dataset_id_1": {
            "s3_url": "https://example.com/s3_url",
            "dataset_recipe": {"files": [{"description": "Test Description"}]},
            "recipe_id": "b2fd5dcf-10e0-4c21-a49c-7c6282b57d93",
        }
    }
    return DatasetAPIClient(url=url, upload_dict=upload_dict)


def setup_mock_token_auth(mock_request):
    """
    Set up the mock token authentication response
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url"
    mock_token_response = MagicMock(spec=Response)
    mock_token_response.status_code = 201
    mock_token_response.headers = {
        "Refresh": "test_refresh_token",
        "Authorization": "test_auth_token",
        "ID": "test_id_token",
    }
    mock_request.return_value = mock_token_response
    return mock_token_response


@patch("requests.request")
def test_get_recipe_id(mock_request):
    """
    Test that the get_recipe_id method correctly retrieves the recipe ID
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "id": "test_recipe_id",
                "output_instances": [{"dataset_id": "dataset_id_1"}],
                "files": [{"description": "Test Description"}],
            }
        ]
    }
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = client()
    mock_client.upload_dict["dataset_id_1"] = {"s3_url": "https://example.com/s3_url"}
    mock_client._get_recipe_id("dataset_id_1")

    # Assert the recipe ID was updated correctly
    assert mock_client.upload_dict["dataset_id_1"]["recipe_id"] == "test_recipe_id"


@patch("requests.request")
def test_post_new_job_success(mock_request):
    """
    Test that the post_new_job method sends the correct payload to the correct URL
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 201
    mock_request.side_effect = [mock_token_response, mock_response]

    # Updated client instantiation and call to match DatasetAPIClient
    upload_dict = {
        "dataset_id": {
            "s3_url": "https://example.com/s3_url",
            "recipe_id": "b2fd5dcf-10e0-4c21-a49c-7c6282b57d93",
            "dataset_recipe": {"files": [{"description": "Test Description"}]},
        }
    }
    mock_client = DatasetAPIClient("http://test_url", upload_dict)
    mock_client.post_new_job()

    expected_payload = {
        "recipe": "b2fd5dcf-10e0-4c21-a49c-7c6282b57d93",
        "state": "created",
        "links": {},
        "files": [
            {"alias_name": "Test Description", "url": "https://example.com/s3_url"}
        ],
    }

    # Assert the request was made correctly
    assert mock_request.call_count == 2
    mock_request.assert_any_call(
        "POST",
        f"{mock_client.dataset_url}/jobs",
        headers={"X-Florence-Token": "test_auth_token", "ID": "test_id_token"},
        json=expected_payload,
        verify=True,
    )


@patch("requests.request")
def test_post_new_job_failure(mock_request):
    """
    Test that the post_new_job method raises an exception when the response status code is not 201
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    # Setup mock responses to simulate failure
    mock_response = MagicMock(Response)
    mock_response.status_code = 400
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = client()
    with pytest.raises(Exception):
        mock_client.post_new_job()


@patch("requests.request")
def test_send_json_success(mock_request):
    """
    Test that the send_json method sends the correct payload to the correct URL
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 201
    mock_response.content = b"Test response content"
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient("http://test_url", {})
    response = mock_client.send_json(mock_client.url, {"key": "value"})

    assert response.status_code == 201
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_with(
        "POST",
        "http://test_url",
        headers=mock_client.token_auth.get_auth_header(),
        json={"key": "value"},
        verify=True,
    )


@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
@patch("requests.request")
def test_upload_json(mock_request, mock_open_file):
    """
    Test that the upload_json method sends the correct payload to the correct URL
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    # Mock the send_json response
    mock_send_response = MagicMock(Response)
    mock_send_response.status_code = 201

    mock_request.side_effect = [mock_token_response, mock_send_response]

    mock_client = DatasetAPIClient("http://test_url", {})
    test_file_path = Path("example/file.json")

    mock_client.upload_json(test_file_path)

    mock_open_file.assert_called_once_with(test_file_path, "r")
    mock_request.assert_called_with(
        "POST",
        "http://test_url",
        headers=mock_client.token_auth.get_auth_header(),
        json={"key": "value"},
        verify=True,
    )


@patch("requests.request")
def test_send_json_failure(mock_request):
    """
    Test that the send_json method raises an exception when the response status code is not 201
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    # Setup mock responses to simulate failure
    mock_response = MagicMock(Response)
    mock_response.status_code = 400
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient("http://test_url", {})
    with pytest.raises(Exception):
        mock_client.send_json(mock_client.url)
