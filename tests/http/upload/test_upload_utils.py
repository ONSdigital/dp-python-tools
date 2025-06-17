import os
from pathlib import Path

from dpytools.http.upload.utils import (
    _create_temp_chunks,
    _delete_temp_chunks,
    _generate_upload_new_params,
)


def test_create_and_delete_temp_chunks():
    """
    Ensures that _create_temp_chunks() creates the correct number of file chunks and that _delete_temp_chunks() deletes the temporary files.
    """
    temp_file_paths_list = _create_temp_chunks(
        file_path=Path("tests/test_cases/countries.csv")
    )
    assert len(temp_file_paths_list) == 2
    assert "temp-file-part-1" in temp_file_paths_list[0]
    _delete_temp_chunks(temp_file_paths_list)
    assert os.path.exists(Path(temp_file_paths_list[0]).absolute()) is False


def test_generate_upload_new_params_for_csv():
    """
    Ensures that _generate_upload_new_params() populates the upload_params dict with the correct values
    """
    identifier = "test-id"
    upload_path = "test/upload/path/here"
    upload_params = _generate_upload_new_params(
        file_path=Path("tests/test_cases/countries.csv"),
        mimetype="text/csv",
        chunk_size=5242880,
        title="title",
        alias_name="alias-name",
        is_publishable=False,
        licence="My licence",
        licence_url="www.example.org/licence",
        collection_id="my-collection-id",
        identifier=identifier,
        upload_path=upload_path,
    )
    assert upload_params["resumableTotalChunks"] == 2
    assert upload_params["resumableTotalSize"] == 6198846
    assert upload_params["resumableType"] == "text/csv"
    assert upload_params["resumableIdentifier"] == identifier
    assert upload_params["resumableFilename"] == "countries.csv"
    assert upload_params["resumableRelativePath"] == "tests/test_cases/countries.csv"
    assert upload_params["aliasName"] == "alias-name"
    assert upload_params["Title"] == "title"
    assert upload_params["Licence"] == "My licence"
    assert upload_params["LicenceUrl"] == "www.example.org/licence"
    assert upload_params["collectionId"] == "my-collection-id"
    assert upload_params["Path"] == upload_path
