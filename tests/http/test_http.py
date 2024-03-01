import pytest
from unittest.mock import patch, MagicMock
from requests import HTTPError, Response
from dpytools.http.base import BaseHttpClient


# Mock the requests.request method
@patch("requests.request")
def test_get(mock_request):
    """
    Test that the get method returns a response object
    """

    # Create a mock response object
    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.content = b"Test response content"
    mock_request.return_value = mock_response

    # Create an instance of BaseHttpClient and make a GET request
    client = BaseHttpClient()
    response = client.get("http://example.com")

    # Assertions to check the response status, content and the request call
    assert response.status_code == 200
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_once_with("GET", "http://example.com")


@patch("requests.request")
def test_post(mock_request):
    """
    Test that the post method returns a response object
    """

    # Create a mock response object
    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_response.content = b"Test response content"
    mock_request.return_value = mock_response

    # Create an instance of BaseHttpClient and make a POST request
    client = BaseHttpClient()
    response = client.post("http://example.com")

    # Assertions to check the response status, content and the request call
    assert response.status_code == 200
    assert response.content.decode() == "Test response content"
    mock_request.assert_called_once_with("POST", "http://example.com")


@patch("requests.request")
def test_backoff_on_exception(mock_request):
    """
    Test that the get method retries on HTTPError
    """

    # Create a mock response object
    mock_response = MagicMock(Response)
    mock_response.status_code = 200

    # Raise HTTPError on the first call, then return the mock_response
    mock_request.side_effect = [HTTPError("HTTP Error"), mock_response]

    # Create an instance of BaseHttpClient and make a GET request
    client = BaseHttpClient()
    response = client.get("http://example.com")

    # Assertions to check the response status and the number of request calls
    assert response.status_code == 200
    assert mock_request.call_count == 2
