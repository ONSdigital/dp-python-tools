from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from dpytools.db.db_collection import DBCollection


class DocumentDBClientOptions:
    """
    Class to organise the arguments needed to connect to a DocumentDB cluster.

    :param host: The host to connect to
    :param port: The port to connect to
    :param username: The username to use for the connection
    :param password: The password associated with the username
    :param connection_string: A full connection string value

    :return: dpytools.db.DocumentDBClientOptions
    """

    def __init__(
        self,
        host: str = "localhost",
        port: str = "27017",
        username: Optional[str] = None,
        password: Optional[str] = None,
        connection_string: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection_string = connection_string

    def get_connection_string(self) -> str:
        """
        Construct the connection string from the client options provided.
        """
        if self.connection_string:
            # If connection_string is passed as a constructor argument (e.g. when using Secrets Manager), set this as the value for self.connection_string
            return self.connection_string
        elif self.host and self.port and self.username and self.password:
            # If connection_string is not passed as a constructor argument, but username and password are set, construct self.connection_string as follows
            self.connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
        elif self.host and self.port and (not self.username or not self.password):
            # If only host and port are set, construct self.connection_string as follows to access a database locally (e.g. using Docker with localhost)
            self.connection_string = f"{self.host}:{self.port}"
        else:
            raise ValueError("Values missing from connection string")
        return self.connection_string


class DocumentDBClient:
    """
    Class to manage DocumentDB connections, databases and collections.

    :param client_options: DocumentDBClientOptions object with the arguments to connect to a specific database.
    :param database_name: The name of the database to connect to.

    :return: dpytools.db.DocumentDBClient
    """

    def __init__(self, client_options: DocumentDBClientOptions, database_name: str):
        self.client_options: DocumentDBClientOptions = client_options
        self.database_name: str = database_name
        self.connection_string: Optional[str] = None
        self.connection: Optional[MongoClient] = None
        self.__database: Optional[Database] = None

    def connect(self, *args, **kwargs) -> MongoClient:
        """
        Connect to MongoDB.

        A `MongoClient` object automatically connects when instantiated (as the MongoClient `connect` parameter is `True` by default).

        :return: pymongo.MongoClient
        """
        self.connection_string = self.client_options.get_connection_string()
        self.connection = MongoClient(host=self.connection_string, *args, **kwargs)
        self.__database = self.connection.get_database(self.database_name)
        if self.__database is None:
            raise ValueError("Error getting database")

        return self.connection

    def close(self) -> None:
        """
        Close the connection.

        :return: None
        """
        if self.connection is not None:
            self.connection.close()

    def get_collection(self, collection_name: str, *args, **kwargs) -> DBCollection:
        """
        Get a collection `collection_name` from the given database.

        :param collection_name: The name of the collection to retrieve (as a string).

        :return: dpytools.db.DBCollection
        """
        if self.__database is None:
            raise ValueError("Error getting database")

        collection = self.__database.get_collection(collection_name, *args, **kwargs)
        return DBCollection(collection)
