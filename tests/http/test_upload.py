import os
from pathlib import Path

from dpytools.http.upload import (
    _create_temp_chunks,
    _delete_temp_chunks,
    _generate_upload_params,
    _generate_upload_new_params,
)


def test_create_and_delete_temp_chunks():
    """
    Ensures that _create_temp_chunks() creates the correct number of file chunks and that _delete_temp_chunks() deletes the temporary files.
    """
    temp_file_paths_list = _create_temp_chunks(
        csv_path="tests/test_cases/countries.csv"
    )
    assert len(temp_file_paths_list) == 2
    assert "temp-file-part-1" in temp_file_paths_list[0]
    _delete_temp_chunks(temp_file_paths_list)
    assert os.path.exists(Path(temp_file_paths_list[0]).absolute()) == False


def test_generate_upload_params():
    """
    Ensures that _generate_upload_params() populates the upload_params dict with the correct values
    """
    upload_params = _generate_upload_params(
        csv_path="tests/test_cases/countries.csv",
        chunk_size=5242880,
    )
    assert upload_params["resumableTotalChunks"] == 2
    assert upload_params["resumableTotalSize"] == 6198846
    assert upload_params["resumableFilename"] == "countries.csv"
    assert "-countries-csv" in upload_params["resumableIdentifier"]


def test_generate_upload_new_params():
    """
    Ensures that _generate_upload_new_params() populates the upload_params dict with the correct values
    """
    upload_params = _generate_upload_new_params(
        csv_path="tests/test_cases/countries.csv",
        s3_path="s3-path",
        collection_id="collection-id",
        title="title",
        # is_publishable=True
    )
    assert upload_params["path"] == "s3-path"
    assert upload_params["collectionId"] == "collection-id"
    assert upload_params["title"] == "title"
    assert upload_params["resumableTotalChunks"] == 2
    assert upload_params["resumableTotalSize"] == 6198846
    assert "-countries-csv" in upload_params["resumableFilename"]
