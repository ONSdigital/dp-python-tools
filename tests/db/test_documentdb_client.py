from unittest.mock import MagicMock, patch
from dpytools.db.documentdb_client import DocumentDBClient


def test_document_db_client():
    """
    Test DocumentDBClient object instantiation.
    """
    client = DocumentDBClient("localhost", 27017)
    assert client.uri == "localhost:27017"
    assert client.connection is None


@patch("dpytools.db.documentdb_client.MongoClient")
def test_connect(mock_MongoClient):
    """
    Test that the `DocumentDBClient.connect` method returns a `MongoClient` object.
    """
    client = DocumentDBClient("localhost", 27017)
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    client.connect()
    assert client.connection == mock_mongo_client


@patch("dpytools.db.documentdb_client.MongoClient")
def test_close(mock_MongoClient):
    """
    Test that the `DocumentDBClient.close` method closes the connection to the database.
    """
    client = DocumentDBClient("localhost", 27017)
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    client.connection = mock_mongo_client
    client.close()
    mock_mongo_client.close.assert_called_once()


@patch("dpytools.db.documentdb_client.MongoClient")
def test_get_database(mock_MongoClient):
    """Test that the `DocumentDBClient.get_database` method calls `get_database` on the `MongoClient`."""
    client = DocumentDBClient("localhost", 27017)
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    client.connection = mock_mongo_client
    client.get_database("test-db")
    mock_mongo_client.get_database.assert_called_once_with("test-db")


@patch("dpytools.db.documentdb_client.Database")
@patch("dpytools.db.documentdb_client.MongoClient")
def test_get_collection(mock_MongoClient, mock_db):
    """
    Test that the `DocumentDBClient.get_collection` method returns a `DBCollection` object.
    """
    client = DocumentDBClient("localhost", 27017)
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    client.connection = mock_mongo_client
    mock_db = MagicMock(name="Database")
    client.get_collection(mock_db, "test-collection")
    mock_db.get_collection.assert_called_once_with("test-collection")
