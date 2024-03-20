import pytest
import boto3
from moto import mock_ses
from dpytools.email.ses.client import SesClient

@pytest.fixture
@mock_ses
def mock_ses_client():
    boto3.setup_default_session(region_name='us-west-2')
    return boto3.client('ses')

@mock_ses
def test_ses_client_initialisation(mock_ses_client):
    """
    Test the initialisation of the SesClient.
    """
    # Initialise the SesClient
    mock_ses_client = SesClient('sender@example.com', 'us-west-2')

    # Assert that the sender is set correctly
    assert mock_ses_client.sender == 'sender@example.com'

    # Assert that the client is not None
    assert mock_ses_client.client is not None

@mock_ses
def test_ses_client_initialisation_invalid_sender_email():
    """
    Test the initialisation of the SesClient with an invalid sender email.
    """
    with pytest.raises(ValueError) as e:
        SesClient('invalid_email', 'us-west-2')
    assert 'Invalid sender email format: invalid_email' in str(e.value)

@mock_ses
def test_ses_client_initialisation_invalid_aws_region():
    """
    Test the initialisation of the SesClient with an invalid AWS region.
    """
    with pytest.raises(ValueError) as e:
        SesClient('sender@example.com', 'invalid_region')
    assert 'Invalid AWS region: invalid_region' in str(e.value)

@mock_ses
def test_ses_client_send_invalid_recipient(mock_ses_client):
    """
    Test the send method of the SesClient with an invalid recipient.
    """
    # Initialise the SES client
    mock_ses_client = SesClient('sender@example.com', 'us-west-2')

    with pytest.raises(ValueError) as e:
        mock_ses_client.send('invalid_email', 'subject', 'body')

    assert 'Invalid recipient email format: invalid_email' in str(e.value)

@mock_ses
def test_ses_client_send_missing_subject(mock_ses_client):
    """
    Test the send method of the SesClient with a missing subject.
    """
    # Initialise the SES client
    mock_ses_client = SesClient('sender@example.com', 'us-west-2')

    with pytest.raises(TypeError) as e:
        mock_ses_client.send('recipient@example.com', None, 'body')
    
    assert 'Missing Subject' in str(e.value)

@mock_ses
def test_ses_client_send_missing_body(mock_ses_client):
    """
    Test the send method of the SesClient with a missing body.
    """
    # Initialise the SES client
    mock_ses_client = SesClient('sender@example.com', 'us-west-2')

    with pytest.raises(TypeError) as e:
        mock_ses_client.send('recipient@example.com', 'subject', None)
        
    assert 'Missing Body' in str(e.value)

@mock_ses
def test_ses_client_send_email(mock_ses_client):
    """
    Test the send method of the SesClient.
    """
    # Initialise the SES client
    mock_ses_client = SesClient('sender@example.com', 'us-west-2')

    # Send an email
    response = mock_ses_client.send('recipient@example.com', 'subject', 'body')

    # Check the HTTP status code in the response
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200