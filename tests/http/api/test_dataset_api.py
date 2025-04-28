import datetime
import os
from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from dpytools.http.api.dataset_api_client import DatasetAPIClient
from dpytools.logging.response_error import (
    DatasetResponseError,
    map_error_json_to_object,
)


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
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_client = DatasetAPIClient(
        "http://test_url", "test_dataset_path", "test_edition_path"
    )
    response = mock_client.post_json({"key": "value"})

    assert response.status_code == 201
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_with(
        "POST",
        "http://test_url/test_dataset_path/editions/test_edition_path/versions",
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

    mock_client = DatasetAPIClient(
        "http://test_url", "test_dataset_path", "test_edition_path"
    )
    with pytest.raises(Exception):
        mock_client.post_json({"key": "value"})


@patch("requests.request")
def test_put_json_success(mock_request):
    """
    Test that the put_json method sends the correct payload to the correct URL
    """
    url = "http://test_url/test_dataset_path/editions/test_edition_path/versions"

    # Mock the token authentication response
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.content = b"Test response content"
    mock_request.side_effect = [mock_token_response, mock_response]
    mock_response.url = url
    mock_response.headers = {
        "Date": str(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
    }
    mock_response.elapsed = datetime.timedelta(seconds=1)

    mock_response_request_mock = MagicMock()
    mock_response.request = mock_response_request_mock
    mock_response_request_mock.method = "PUT"

    mock_client = DatasetAPIClient(
        "http://test_url", "test_dataset_path", "test_edition_path"
    )
    response = mock_client.put_json({"key": "value"})

    assert response.status_code == 200
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_with(
        "PUT",
        url,
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

    mock_client = DatasetAPIClient(
        "http://test_url", "test_dataset_path", "test_edition_path"
    )
    with pytest.raises(Exception):
        mock_client.put_json({"key": "value"})


@patch("requests.request")
def test_get_path_success(mock_request):
    url = "http://test_url/test_dataset_path/editions/test_edition_path/versions"
    mock_token_response = setup_mock_token_auth(mock_request)

    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.content = b"Test response content"
    mock_request.side_effect = [mock_token_response, mock_response]

    mock_response.url = url
    mock_response.headers = {
        "Date": str(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
    }
    mock_response.elapsed = datetime.timedelta(seconds=1)

    mock_response_request_mock = MagicMock()
    mock_response.request = mock_response_request_mock
    mock_response_request_mock.method = "GET"

    mock_client = DatasetAPIClient(
        "http://test_url", "test_dataset_path", "test_edition_path"
    )
    response = mock_client.get_path(params={"key": "value"})
    assert response.status_code == 200
    # Verify response content
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_with(
        "GET",
        url,
        headers=mock_client.token_auth.get_auth_header(),
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

    test_error_response = map_error_json_to_object(error_dict)

    assert test_error_response
    assert test_error_response.cause == "Error cause"
    assert test_error_response.error_code == "TestErrorCode"
    assert test_error_response.description == "Error description"


def test_map_error_json_to_object_wrong_field():
    """
    Tests that the expected error is raised when an input dict is given 
    to create a DatasetResponseError object, but the fields in the dict
    do not match the structure for an error response.
    """
    error_dict = {
        "Wrong field": "Error message"
    }

    with pytest.raises(ValueError) as e:
        map_error_json_to_object(error_dict)
    
    assert "Error dict does not contain expected error keys (Cause, Code, Description). Dictionary contents: {'Wrong field': 'Error message'}" == str(e.value)


def test_map_error_json_to_object_missing_field():
    """
    Tests that the expected error is raised when an input dict is given
    to create a DatasetResponseError object, with correct fields for an
    error response, but an expected field is missing.
    """
    error_dict = {
        "Cause": "Error cause",
        "Code": "TestErrorCode",
    }

    with pytest.raises(ValueError) as e:
        map_error_json_to_object(error_dict)
    
    assert "Error dict does not contain expected error keys (Cause, Code, Description). Dictionary contents: {'Cause': 'Error cause', 'Code': 'TestErrorCode'}" == str(e.value)