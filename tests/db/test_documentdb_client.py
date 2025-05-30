from unittest.mock import MagicMock, patch

import pytest
from dpytools.db.db_collection import DBCollection
from dpytools.db.documentdb_client import DocumentDBClient, DocumentDBClientOptions


def test_document_db_client_options_with_connection_string():
    client_options = DocumentDBClientOptions(
        connection_string="mongodb://username:password@cluster.node.localhost:27017?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false",
    )
    connection_string = client_options.get_connection_string()
    assert (
        connection_string
        == "mongodb://username:password@cluster.node.localhost:27017?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
    )


def test_document_db_client_options_with_username():
    client_options = DocumentDBClientOptions(
        host="cluster.node.localhost",
        port="27017",
        username="username",
        password="password",
    )
    connection_string = client_options.get_connection_string()
    assert (
        connection_string
        == "mongodb://username:password@cluster.node.localhost:27017?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
    )


def test_document_db_client_options_without_username():
    client_options = DocumentDBClientOptions(
        host="localhost",
        port="27017",
    )
    connection_string = client_options.get_connection_string()
    assert connection_string == "localhost:27017"


def test_document_db_client_options_default():
    client_options = DocumentDBClientOptions()
    connection_string = client_options.get_connection_string()
    assert connection_string == "localhost:27017"


def test_document_db_client():
    """
    Test DocumentDBClient object instantiation.
    """
    client_options = DocumentDBClientOptions(host="localhost", port="27017")
    client = DocumentDBClient(client_options, "test-db")

    assert client.database_name == "test-db"


@patch("dpytools.db.documentdb_client.MongoClient")
def test_connect(mock_MongoClient):
    """
    Test that the `DocumentDBClient.connect` method returns a `MongoClient` object.
    """
    client_options = DocumentDBClientOptions(host="localhost", port="27017")
    client = DocumentDBClient(client_options, "test-db")
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    client.connect()

    assert client.connection == mock_mongo_client
    assert client.connection_string == "localhost:27017"


@patch("dpytools.db.documentdb_client.MongoClient")
def test_close(mock_MongoClient):
    """
    Test that the `DocumentDBClient.close` method closes the connection to the database.
    """
    client_options = DocumentDBClientOptions(host="localhost", port="27017")
    client = DocumentDBClient(client_options, "test-db")
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    client.connection = mock_mongo_client
    client.close()

    mock_mongo_client.close.assert_called_once()


@patch("dpytools.db.documentdb_client.MongoClient")
def test_get_collection(mock_MongoClient):
    """
    Test that the `DocumentDBClient.get_collection` method returns a `DBCollection` object.
    """
    client_options = DocumentDBClientOptions(host="localhost", port="27017")
    client = DocumentDBClient(client_options, "test-db")
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    client.connect()
    collection = client.get_collection("test-collection")

    assert isinstance(collection, DBCollection)
    mock_mongo_client.get_database.assert_called_once_with("test-db")
    mock_mongo_client.get_database.return_value.get_collection.assert_called_once_with(
        "test-collection"
    )


@patch("dpytools.db.documentdb_client.MongoClient")
def test_connect_no_database(mock_MongoClient):
    """
    Test that a ValueError is raised if the specified database is not found when calling the connect() method.
    """
    client_options = DocumentDBClientOptions(host="localhost", port="27017")
    client = DocumentDBClient(client_options, "test-db")
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    mock_mongo_client.get_database.return_value = None
    with pytest.raises(ValueError) as e:
        client.connect()
    assert "Error getting database" in str(e)


@patch("dpytools.db.documentdb_client.MongoClient")
def test_get_collection_no_database(mock_MongoClient):
    """
    Test that a ValueError is raised if the specified database is not found when calling the connect() method.
    """
    client_options = DocumentDBClientOptions(host="localhost", port="27017")
    client = DocumentDBClient(client_options, "test-db")
    mock_mongo_client = MagicMock(name="MongoClient")
    mock_MongoClient.return_value = mock_mongo_client
    mock_mongo_client.get_database.return_value = None
    with pytest.raises(ValueError) as e:
        client.get_collection("test-collection")
    assert "Error getting database" in str(e)
