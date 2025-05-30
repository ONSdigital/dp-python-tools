# dpytools: Databases

## Usage

These database clients provide a set of tools for interacting with MongoDB databases, including managing database connections, getting databases and collections, and performing database operations (create/read/update) on specified collections.

### DocumentDBClient

The `DocumentDBClient` class facilitates the process of connecting to a MongoDB database by allowing users to specify the arguments required to connect to a database. These arguments are provided in the form of a `DocumentDBClientOptions` object. This allows users to configure database access according to their own needs (e.g. connect to a local instance using Docker, or provide a full connection string using AWS Secrets Manager).

Calling the `DocumentDBClient.connect()` method creates a `pymongo.MongoClient`, which automatically connects to the specified database. The example below shows a local database running in a Docker container. To replicate this run the following command in the terminal:

`docker run -d -p 27017:27017 --name mongo-db mongo:latest`

```python
from dpytools.db.documentdb_client import DocumentDBClient, DocumentDBClientOptions

client_options = DocumentDBClientOptions(
    host="localhost",
    port="27017",
)
client = DocumentDBClient(
    client_options=client_options,
    database_name="state")
client.connect()

# Additional args and kwargs can be passed to the `connect()` method depending on the configuration of the target database
# E.g., specify `uuidRepresentation="standard`:
client.connect(uuidRepresentation="standard")
```

The client also has a `get_collection()` method:

```python
collection = client.get_collection(
    collection_name="test-collection"
)
```

This method returns a `DBCollection` object, which is a thin wrapper for a `pymongo.synchronous.Collection` object - see the [DBCollection](#dbcollection) section for more details.

Finally, there is a `close()` method provided to close the connection:

```python
client.close()
```

### DBCollection

The `DBCollection` class provides methods for creating, reading and updating collection documents. The examples below assume that you have already created a `DBCollection` object named `collection`, and that the structure of a single document is as follows:

```python
{
    "dataset_id": "dataset_id_1",
    "latest_edition_id": "edition_id_for_dataset_id_1",
    "latest_version_id": 3,
    "created_at": "2025-06-08T07:10:54.785Z",
    "statuses": {
        "status_id_1": {
            "status": "pending"
        }
    }
}
```

#### `create_one_document`

To create one document in the collection, use the `create_one_document` method:

```python
document = {
    "dataset_id": "dataset_id_1",
    "latest_edition_id": "edition_id_for_dataset_id_1",
    "latest_version_id": 3,
    "created_at": "2025-06-08T07:10:54.785Z",
    "statuses": {
        "status_id_1": {
            "status": "pending"
        }
    }
}

result = collection.create_one_document(document=document)
# Returns pymongo.results.InsertOneResult
```

#### `read_one_document`

To find one document in the collection, use the `read_one_document` method. If more than one document in the collection matches the filter, only the first match will be returned.

In the example below, we wish to find one document with a `dataset_id` of "dataset_id_1":

```python
result = collection.read_one_document(
    filter_by={"dataset_id": "dataset_id_1"}
)

# Returns a dictionary representing a single matching document:
{
    "dataset_id": "dataset_id_1",
    "latest_edition_id": "edition_id_for_dataset_id_1",
    "latest_version_id": 3,
    "created_at": "2025-06-08T07:10:54.785Z",
    "statuses": {
        "status_id_1": {
            "status": "pending"
        }
    }
}
```

#### `update_one_document`

To update a single document in the collection, use the `update_one_document` method. 

In the example below, the document to be updated has a `dataset_id` of "dataset_id_1". The value to be updated is the `latest_edition_id`, which we want to change to "new_edition_id_for_dataset_id_1":

```python
result = collection.update_one_document(
    filter_by={
        "dataset_id": "dataset_id_1"
    },
    update_values={
        "latest_edition_id": "new_edition_id_for_dataset_id_1"
    }
)
# Returns a pymongo.results.UpdateResult
```

#### `create_many_documents`

To create multiple documents in a collection, use the `create_many_documents` method.

```python
documents = [
    {
        "dataset_id": "dataset_id_1",
        "latest_edition_id": "edition_id_for_dataset_id_1",
        "latest_version_id": 3,
        "created_at": "2025-06-08T07:10:54.785Z",
        "statuses": {
            "status_id_1": {
                "status": "pending"
            }
        }
    },
        {
        "dataset_id": "dataset_id_2",
        "latest_edition_id": "edition_id_for_dataset_id_2",
        "latest_version_id": 1,
        "created_at": "2025-04-29T10:23:45.564Z",
        "statuses": {
            "status_id_1": {
                "status": "processing"
            }
        }
    }
    ...
]

result = collection.create_many_documents(documents=documents)
# Returns a pymongo.results.InsertManyResult
```

#### `read_many_documents`

To find multiple documents in a collection that match a specific filter, use the `read_many_documents` method.

In the example below, there are multiple documents in the collection with a `dataset_id` of "dataset_id_1":

```python
result = collection.read_many_documents(
    {"dataset_id": "dataset_id_1"}
)

# Returns a list of dictionaries where each dictionary represents a single matching document:
[
    {
        "dataset_id": "dataset_id_1",
        "latest_edition_id": "edition_id_for_dataset_id_1",
        "latest_version_id": 3,
        "created_at": "2025-06-08T07:10:54.785Z",
        "statuses": {
            "status_id_1": {
                "status": "pending"
            }
        }
    },
    {
        "dataset_id": "dataset_id_1",
        "latest_edition_id": "other_edition_id_for_dataset_id_1",
        "latest_version_id": 2,
        "created_at": "2025-04-29T10:23:45.564Z",
        "statuses": {
            "status_id_1": {
                "status": "processing"
            }
        }
    }
    ...
]
```

#### `update_many_documents`

To update multiple documents in a collection that match a specific filter, use the `update_many_documents` method.

In the example below, there are multiple documents in the collection with a `dataset_id` of "dataset_id_1":

```python
result = collection.update_many_documents(
    filter_by={
        "dataset_id": "dataset_id_1"
    },
    update_values={
        "latest_edition_id": "new_edition_id_for_dataset_id_1"
    },
)
# Returns a pymongo.results.UpdateResult
```
