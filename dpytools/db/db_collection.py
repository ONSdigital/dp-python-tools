from pymongo.synchronous.collection import Collection
from typing import Dict, List, Optional
from pymongo.results import InsertOneResult, UpdateResult, InsertManyResult


class DBCollection:
    def __init__(self, collection: Collection):
        self.__collection = collection

    def create_one_document(self, document: Dict) -> InsertOneResult:
        """
        Create one new document in the specified collection.

        :param document: A dictionary containing the fields (keys) and values to create one new document in the collection.

        :return: pymongo.results.InsertOneResult
        """
        return self.__collection.insert_one(document)

    def read_one_document(self, filter_by: Dict) -> Optional[Dict]:
        """
        Read one document in the specified collection that matches the given filter. If there is more than one document that matches the filter, only the first result will be returned.

        :param filter_by: A dictionary where the keys are the fields to search in the collection, and the values are the values to match within these fields.

        :return: A dictionary representing a single document from the collection.
        """
        return self.__collection.find_one(filter=filter_by)

    def update_one_document(self, filter_by: Dict, update_values: Dict) -> UpdateResult:
        """
        Update one document in the specified collection that matches the given filter.

        :param filter_by: A dictionary where the keys are the fields to search in the collection, and the values are the values to match within these fields.

        :param update_values: A dictionary where the keys are the fields to update in the matching document, and the values are the values to update within these fields.

        :return: pymongo.results.UpdateResult
        """
        return self.__collection.update_one(
            filter=filter_by, update={"$set": update_values}
        )

    def create_many_documents(self, documents: List[Dict]) -> InsertManyResult:
        """
        Create multiple new documents in the specified collection.

        :param documents: A list of dictionaries containing the fields (keys) and values to create multiple new documents in the collection.

        :return: pymongo.results.InsertManyResult
        """
        return self.__collection.insert_many(documents)

    def read_many_documents(
        self, filter_by: Optional[Dict] = None
    ) -> Optional[List[Dict]]:
        """
        Read multiple documents in the specified collection that match the given filter.

        :param filter_by: A dictionary where the keys are the fields to search in the collection, and the values are the values to match within these fields.

        :return: A list of dictionaries, each of which represents one document in the collection.
        """
        if not filter_by:
            filter_by = {}
        return [res for res in self.__collection.find(filter=filter_by)]

    def update_many_documents(
        self, filter_by: Dict, update_values: Dict
    ) -> UpdateResult:
        """
        Update multiple documents in the specified collection that match the given filter.

        :param filter_by: A dictionary where the keys are the fields to search in the collection, and the values are the values to match within these fields.

        :param update_values: A dictionary where the keys are the fields to update in the matching documents, and the values are the values to update within these fields.

        :return: pymongo.results.UpdateResult
        """
        return self.__collection.update_many(
            filter=filter_by, update={"$set": update_values}
        )
