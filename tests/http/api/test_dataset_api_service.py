import unittest
from unittest.mock import Mock, patch

import pytest

from dpytools.http.base_http import BaseHttpClient
from dpytools.http.token_auth import TokenAuth
from dpytools.logging.logger import DpLogger
from dpytools.http.api.versions.dataset_versions_service import DatasetVersionsService
from dpytools.http.api.datasets.datasets_service import DatasetsService
from dpytools.http.api.dataset_api_service import DatasetAPIService  # Assuming the class is in this module


@patch('dpytools.http.api.dataset_api_service.DpLogger')
@patch('dpytools.http.api.dataset_api_service.BaseHttpClient')
@patch('dpytools.http.api.dataset_api_service.TokenAuth')
@patch('dpytools.http.api.dataset_api_service.DatasetVersionsService')
@patch('dpytools.http.api.dataset_api_service.DatasetsService')
def test_init_with_trailing_slash(mock_datasets_service, mock_versions_service, 
                                mock_token_auth, mock_http_client, mock_logger):
    """Test initialization with URL that has a trailing slash."""
    # Arrange
    dataset_api_url = "https://api.example.com/datasets/"
    expected_url = "https://api.example.com/datasets"
    
    # Act
    service = DatasetAPIService(dataset_api_url)
    
    # Assert
    mock_logger.assert_called_once_with("DatasetAPIClient")
    mock_http_client.assert_called_once()
    mock_token_auth.assert_called_once()
    
    mock_versions_service.assert_called_once_with(
        expected_url, 
        mock_logger.return_value, 
        mock_http_client.return_value, 
        mock_token_auth.return_value
    )
    
    mock_datasets_service.assert_called_once_with(
        expected_url, 
        mock_logger.return_value, 
        mock_http_client.return_value, 
        mock_token_auth.return_value
    )
    
    assert service.dataset_api_url == expected_url
    assert isinstance(service.versions, Mock)
    assert isinstance(service.datasets, Mock)

test_urls = [
    "https://api.example.com/datasets",
    "https://api.example.com/datasets/"
]

@pytest.mark.parametrize("dataset_api_url", test_urls)
@patch('dpytools.http.api.dataset_api_service.DpLogger')
@patch('dpytools.http.api.dataset_api_service.BaseHttpClient')
@patch('dpytools.http.api.dataset_api_service.TokenAuth')
@patch('dpytools.http.api.dataset_api_service.DatasetVersionsService')
@patch('dpytools.http.api.dataset_api_service.DatasetsService')
def test_init_handles_url(mock_datasets_service, mock_versions_service, mock_token_auth, mock_http_client, mock_logger, dataset_api_url):
    """
    Test initialization with URL that does not have a trailing slash.
    """
    expected_dataset_api_url = "https://api.example.com/datasets"
    
    service = DatasetAPIService(dataset_api_url)
    
    mock_logger.assert_called_once_with("DatasetAPIClient")
    mock_http_client.assert_called_once()
    mock_token_auth.assert_called_once()
    
    mock_versions_service.assert_called_once_with(
        expected_dataset_api_url, 
        mock_logger.return_value, 
        mock_http_client.return_value, 
        mock_token_auth.return_value
    )
    
    mock_datasets_service.assert_called_once_with(
        expected_dataset_api_url, 
        mock_logger.return_value, 
        mock_http_client.return_value, 
        mock_token_auth.return_value
    )
    
    assert service.dataset_api_url == expected_dataset_api_url


def test_integration(monkeypatch):
    """
    Test actual integration of components without mocking.
    """
    monkeypatch.setenv("SERVICE_TOKEN_FOR_UPLOAD", "some-dummy-token")
    dataset_api_url = "https://api.example.com/datasets"
    
    service = DatasetAPIService(dataset_api_url)
    
    assert isinstance(service._logger, DpLogger)
    assert isinstance(service._http_client, BaseHttpClient)
    assert isinstance(service._token_auth, TokenAuth)
    assert isinstance(service.versions, DatasetVersionsService)
    assert isinstance(service.datasets, DatasetsService)
    assert service.dataset_api_url == dataset_api_url