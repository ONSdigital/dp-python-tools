import os
from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from dpytools.http.api.dataset_api_client import DatasetAPIClient


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
        "Authorization": "Bearer test_auth_token",
        "ID": "test_id_token",
    }
    mock_request.return_value = mock_token_response
    return mock_token_response


@patch("requests.request")
def test_post_json_success(mock_request):
    """
    Test that the post_json method sends the correct payload to the correct URL
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 201
    mock_response.content = b"Test response content"
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient("http://test_url", "test_path")
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

    mock_client = DatasetAPIClient("http://test_url", "test_path")
    with pytest.raises(Exception):
        mock_client.post_json({"key": "value"})


@patch("requests.request")
def test_put_json_success(mock_request):
    """
    Test that the put_json method sends the correct payload to the correct URL
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.content = b"Test response content"
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient("http://test_url", "test_path")
    response = mock_client.put_json({"key": "value"})

    assert response.status_code == 200
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_with(
        "PUT",
        "http://test_url/test_path",
        headers=mock_client.token_auth.get_auth_header(),
        json={"key": "value"},
        verify=True,
    )


@patch("requests.request")
def test_put_json_failure(mock_request):
    """
    Test that the put_json method raises an exception when the response status code is not 200
    """
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    # Setup mock responses to simulate failure
    mock_response = MagicMock(Response)
    mock_response.status_code = 400
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient("http://test_url", "test_path")
    with pytest.raises(Exception):
        mock_client.put_json({"key": "value"})


@patch("requests.request")
def test_get_path_success(mock_request):
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.content = b"Test response content"
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient("http://test_url/", "test_path")
    response = mock_client.get_path(params={"key": "value"})
    assert response.status_code == 200
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_with(
        "GET",
        "http://test_url/test_path",
        headers=mock_client.token_auth.get_auth_header(),
        params={"key": "value"},
        verify=True,
    )


@patch("requests.request")
def test_get_path_failure(mock_request):
    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    # Setup mock responses to simulate failure
    mock_response = MagicMock(Response)
    mock_response.status_code = 404
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient("http://test_url/", "test_path")
    with pytest.raises(Exception):
        mock_client.get_path(params={"key": "value"})
