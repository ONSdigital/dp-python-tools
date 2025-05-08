from datetime import datetime as dt
from random import choice, randint
from typing import Dict, List
from pymongo.synchronous.collection import Collection


def insert_test_data(collection: Collection, duplicate: bool = False) -> List[Dict]:
    """
    Insert test data into a pymongo.Collection.

    :param collection: A pymongo.synchronous.Collection.
    :param duplicate: A boolean indicating whether or not to duplicate the test documents inserted into the collection.

    :return: A list of dictionaries representing the documents inserted into the collection.
    """
    statuses = ["pending", "processing", "failed", "completed"]
    test_datasets = [
        {
            "dataset_id": f"dataset_id_{i}",
            "latest_edition_id": f"edition_id_for_dataset_id_{i}",
            "latest_version_id": randint(0, 9),
            "created_at": dt.now().isoformat(),
            "statuses": {
                f"status_id_{j}": {"status": choice(statuses)} for j in range(3)
            },
        }
        for i in range(5)
    ]
    if duplicate:
        test_datasets.extend(
            [
                {
                    "dataset_id": f"dataset_id_{i}",
                    "latest_edition_id": f"edition_id_for_dataset_id_{i}",
                    "latest_version_id": randint(0, 9),
                    "created_at": dt.now().isoformat(),
                    "statuses": {
                        f"status_id_{j}": {"status": choice(statuses)} for j in range(3)
                    },
                }
                for i in range(5)
            ]
        )
    # Insert all documents into the collection and add the inserted ObjectId to the dataset dictionary
    for dataset in test_datasets:
        dataset["_id"] = collection.insert_one(dataset).inserted_id
    return test_datasets
