from random import randint

import mongomock
import pytest
from dpytools.db.db_collection import DBCollection

from datetime import datetime as dt

from tests.fixtures.insert_test_data import insert_test_data


@pytest.fixture
def mock_collection_without_data():
    return mongomock.MongoClient().db.collection


@pytest.fixture
def mock_collection_with_data():
    mock_collection = mongomock.MongoClient().db.collection
    insert_test_data(mock_collection)
    return mock_collection


@pytest.fixture
def mock_collection_with_duplicate_data():
    mock_collection = mongomock.MongoClient().db.collection
    # Duplicate test data so that there are multiple records that match the same filter
    insert_test_data(mock_collection, duplicate=True)
    return mock_collection


@pytest.fixture
def db_collection_without_data(mock_collection_without_data):
    return DBCollection(mock_collection_without_data)


@pytest.fixture
def db_collection_with_data(mock_collection_with_data):
    return DBCollection(mock_collection_with_data)


@pytest.fixture
def db_collection_with_duplicate_data(mock_collection_with_duplicate_data):
    return DBCollection(mock_collection_with_duplicate_data)


def test_create_one_document(mock_collection_without_data, db_collection_without_data):
    """
    Test that `DBCollection.create_one_document` creates one document in the collection.
    """
    db_collection_without_data.create_one_document(
        {
            "dataset_id": "dataset_id_1",
            "latest_edition_id": "edition_id_1",
            "latest_version_id": 1,
            "created_at": dt.now().isoformat(),
            "statuses": {},
        }
    )
    result = mock_collection_without_data.find_one({"dataset_id": "dataset_id_1"})

    assert result["latest_edition_id"] == "edition_id_1"


def test_read_one_document(db_collection_with_data):
    """
    Test that `DBCollection.read_one_document` returns the correct result for the given filter.
    """
    result = db_collection_with_data.read_one_document({"dataset_id": "dataset_id_3"})

    assert result["latest_edition_id"] == "edition_id_for_dataset_id_3"


def test_update_one_document(mock_collection_with_data, db_collection_with_data):
    """
    Test that `DBCollection.update_one_document` updates the specified document with the correct values.
    """
    db_collection_with_data.update_one_document(
        {"dataset_id": "dataset_id_2"},
        {"latest_edition_id": "new_edition_id_for_dataset_id_2"},
    )
    result = mock_collection_with_data.find_one({"dataset_id": "dataset_id_2"})

    assert result["latest_edition_id"] == "new_edition_id_for_dataset_id_2"


def test_create_many_documents(
    mock_collection_without_data, db_collection_without_data
):
    """
    Test that `DBCollection.create_many_documents` creates multiple documents in the specified collection.
    """
    test_datasets = [
        {
            "dataset_id": f"dataset_id_{i}",
            "latest_edition_id": f"edition_id_for_dataset_id_{i}",
            "latest_version_id": randint(0, 9),
            "created_at": dt.now().isoformat(),
            "statuses": {},
        }
        for i in range(5)
    ]
    db_collection_without_data.create_many_documents(test_datasets)

    assert mock_collection_without_data.count_documents({}) == 5


def test_read_many_documents_with_filter(db_collection_with_duplicate_data):
    """
    Test that `DBCollection.read_many_documents` returns multiple results that match the given filter values.
    """
    results_list = db_collection_with_duplicate_data.read_many_documents(
        {"dataset_id": "dataset_id_1"}
    )

    assert len(results_list) == 2


def test_read_many_documents_without_filter(db_collection_with_data):
    results_list = db_collection_with_data.read_many_documents()

    assert len(results_list) == 5


def test_update_many_documents(db_collection_with_duplicate_data):
    """
    Test that `DBCollection.update_many_documents` updates multiple records for the given filter and values to update.
    """
    result = db_collection_with_duplicate_data.update_many_documents(
        {"dataset_id": "dataset_id_4"},
        {"latest_edition_id": "new_edition_id_for_dataset_id_4"},
    )
    results_list = db_collection_with_duplicate_data.read_many_documents(
        {"dataset_id": "dataset_id_4"}
    )

    assert result.matched_count == 2
    assert result.modified_count == 2
    for res in results_list:
        assert res["latest_edition_id"] == "new_edition_id_for_dataset_id_4"
