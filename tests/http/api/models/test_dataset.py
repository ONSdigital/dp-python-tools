from dpytools.http.api.models.dataset import GetDatasetResponse

publishable_dataset_version = {"type": "static", "state": "published"}


def test_dataset_can_publish_new_version_with_just_current():
    dataset = GetDatasetResponse(
        id="dataset_id", current={**publishable_dataset_version}
    )

    assert dataset.can_publish_new_version() is True


def test_dataset_can_publish_new_version_with_current_and_next():
    dataset = GetDatasetResponse(
        id="dataset_id",
        current={**publishable_dataset_version},
        next={**publishable_dataset_version},
    )

    assert dataset.can_publish_new_version() is True


def test_dataset_cant_publish_if_either_type_is_not_static():
    dataset = GetDatasetResponse(
        id="dataset_id",
        current={**publishable_dataset_version, "type": "filterable"},
        next={**publishable_dataset_version},
    )

    assert dataset.can_publish_new_version() is False

    dataset = GetDatasetResponse(
        id="dataset_id",
        current={**publishable_dataset_version},
        next={**publishable_dataset_version, "type": "filterable"},
    )

    assert dataset.can_publish_new_version() is False


def test_dataset_cant_publish_if_either_type_is_not_published():
    dataset = GetDatasetResponse(
        id="dataset_id",
        current={**publishable_dataset_version, "state": "created"},
        next={**publishable_dataset_version},
    )
    assert dataset.can_publish_new_version() is False

    dataset = GetDatasetResponse(
        id="dataset_id",
        current={**publishable_dataset_version},
        next={**publishable_dataset_version, "state": "created"},
    )
    assert dataset.can_publish_new_version() is False
