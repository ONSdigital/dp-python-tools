import pytest
from unittest.mock import patch, MagicMock
from requests import HTTPError, Response
from dpytools.http.base import BaseHttpClient
from dpytools.slack.slack import SlackMessenger


@patch.object(BaseHttpClient, "post")
def test_notify(mock_post):
    """
    Test that the notify method sends a POST request
    """
    webhook_url = "http://example.com"
    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    notifier = SlackMessenger(webhook_url)
    notifier.msg({"text": "Test message"})

    mock_post.assert_called_once_with(webhook_url, json={"text": "Test message"})


@patch.object(BaseHttpClient, "post")
def test_msg_str(mock_post):
    """
    Test that the msg_str method sends a POST request with a string message
    """
    webhook_url = "http://example.com"
    mock_response = MagicMock(Response)
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    notifier = SlackMessenger(webhook_url)
    notifier.msg_str("Test message")

    mock_post.assert_called_once_with(webhook_url, json={"text": "Test message"})
