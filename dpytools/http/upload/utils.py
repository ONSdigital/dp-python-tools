import os
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory


def _generate_upload_new_params(
    file_path: Path,
    mimetype: str,
    chunk_size: int,
    alias_name: str,
    title: str,
    is_publishable: bool,
    licence: str,
    licence_url: str,
    collection_id: str,
    upload_path: str,
    identifier: str,
) -> dict:
    """
    Generate request parameters that do not change when iterating through the list of file chunks.

    To be used with the `upload-new` endpoint.
    """
    # Get total size of file to be uploaded
    total_size = os.path.getsize(file_path)

    file_name = file_path.name.replace(" ", "_")
    # Generate upload request params
    upload_params = {
        "resumableFilename": file_name,
        "resumableType": mimetype,
        "resumableTotalChunks": ceil(total_size / chunk_size),
        "resumableChunkSize": chunk_size,
        "aliasName": alias_name,
        "resumableTotalSize": total_size,
        "resumableIdentifier": identifier,
        "resumableRelativePath": str(file_path),
        "LicenceUrl": licence_url,
        "isPublishable": is_publishable,
        "Title": title,
        "Type": mimetype,
        "Licence": licence,
        "Path": upload_path,
        # TODO: Get collectionId from metadata?
        "collectionId": collection_id,
    }
    return upload_params


def _create_temp_chunks(
    file_path: Path,
    chunk_size: int = 5242880,
) -> list[str]:
    """
    Chunks up the data into text files, saves them to a temporary directory and returns list of temp filenames
    """
    chunk_number = 1
    temp_file_paths_list = []

    # Create TemporaryDirectory to store temporary file chunks
    with TemporaryDirectory() as output_path:
        with open(file_path, "rb") as f:
            # Read chunk according to specified chunk size
            chunk = f.read(chunk_size)
            while chunk:
                # Create temporary filepath
                temp_file_path = f"{output_path}-temp-file-part-{str(chunk_number)}"
                # Write chunk to temporary filepath and append filename to list
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(chunk)
                    temp_file_paths_list.append(temp_file_path)
                chunk_number += 1
                chunk = f.read(chunk_size)
    # Return list of temporary filepaths
    return temp_file_paths_list


def _delete_temp_chunks(temp_file_paths_list: list):
    """
    Deletes the temporary chunks that were uploaded
    """
    for file in temp_file_paths_list:
        os.remove(file)
