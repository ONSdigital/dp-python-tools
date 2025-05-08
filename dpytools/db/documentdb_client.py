from pymongo import MongoClient
from pymongo.synchronous.database import Database

from dpytools.db.db_collection import DBCollection


class DocumentDBClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.uri = f"{host}:{port}"
        self.connection = None

    def connect(self, *args, **kwargs) -> MongoClient:
        """
        Connect to MongoDB.

        A `MongoClient` object automatically connects when instantiated (as the MongoClient `connect` parameter is `True` by default).

        :return: pymongo.MongoClient
        """
        self.connection = MongoClient(self.uri, *args, **kwargs)
        return self.connection

    def close(self) -> None:
        """
        Close the connection.

        :return: None
        """
        if self.connection is not None:
            self.connection.close()

    def get_database(self, db_name: str, *args, **kwargs) -> Database:
        """
        Get a database with the specified `db_name`.

        :param db_name: The name of the database to retrieve (as a string).

        :return: pymongo.synchronous.Database
        """
        return self.connection.get_database(db_name, *args, **kwargs)

    def get_collection(
        self, db: Database, collection_name: str, *args, **kwargs
    ) -> DBCollection:
        """
        Get a collection `collection_name` from the given database.

        :param db: A pymongo.synchronous.Database which contains the specified collection.

        :param collection_name: The name of the collection to retrieve (as a string).

        :return: pymongo.synchronous.Collection
        """
        collection = db.get_collection(collection_name, *args, **kwargs)
        return DBCollection(collection)
