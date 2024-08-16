import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from requests import Response

from dpytools.http.dataset.base_api import BaseAPIClient
from dpytools.http.dataset.dataset_api_client import DatasetAPIClient


def setup_mock_token_auth(mock_request):
    """
    Set up the mock token authentication response
    """
    os.environ["FLORENCE_USER"] = "test_user"
    os.environ["FLORENCE_PASSWORD"] = "test_password"
    os.environ["IDENTITY_API_URL"] = "http://test_url/test-path"
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
def test_post_json_success(mock_request):
    """
    Test that the send_json method sends the correct payload to the correct URL
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 201
    mock_response.content = b"Test response content"
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = BaseAPIClient("test_url", "test_path")
    response = mock_client.post_json({"key": "value"})

    assert response.status_code == 201
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_with(
        "POST",
        "http://test_url/test_path",
        headers=mock_client.token_auth.get_auth_header(),
        json={"key": "value"},
        verify=True,
    )


@patch("requests.request")
def test_post_json_failure(mock_request):
    """
    Test that the post_json method raises an exception when the response status code is not 201
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    # Setup mock responses to simulate failure
    mock_response = MagicMock(Response)
    mock_response.status_code = 400
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = BaseAPIClient("test_url", "test_path")
    with pytest.raises(Exception):
        mock_client.post_json()


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
    mock_client = DatasetAPIClient("test_url", "test_path")
    mock_client.post_new_job()

    assert mock_request.call_count == 2


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

    mock_client = DatasetAPIClient("test_url", "test_path")
    with pytest.raises(Exception):
        mock_client.post_new_job()


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

    mock_client = DatasetAPIClient("test_url", "test_path")
    test_file_path = Path("example/file.json")

    mock_client.upload_json(test_file_path)

    mock_open_file.assert_called_once_with(test_file_path, "r")
    mock_request.assert_called_with(
        "POST",
        "http://test_url/test_path",
        headers=mock_client.token_auth.get_auth_header(),
        json={"key": "value"},
        verify=True,
    )
