import datetime
from math import ceil
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple, Union

from dpytools.http.base import BaseHttpClient


class UploadClient(BaseHttpClient):
    def __init__(self, upload_url: str):
        # Inherit backoff_max value from BaseHTTPClient.__init__
        super().__init__()
        self.upload_url = upload_url

    def upload(
        self,
        csv_path: Union[Path, str],
        s3_bucket: str,
        florence_access_token: str,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload files to the DP Upload Service `upload` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        The `s3_bucket` and `florence_access_token` arguments should be set as environment variables and accessed via os.getenv() or similar.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        # Create file chunks
        file_chunks = _create_temp_chunks(csv_path=csv_path, chunk_size=chunk_size)

        # Generate upload request params
        upload_params = _generate_upload_params(csv_path, chunk_size)

        chunk_number = 1

        for file_chunk in file_chunks:
            with open(file_chunk, "rb") as f:
                # Load file chunk as binary data
                file = {"file": f}

                # Add chunk number to upload request params
                upload_params["resumableChunkNumber"] = chunk_number

                # Submit `POST` request to `self.upload_url`
                self.post(
                    url=self.upload_url,
                    headers={"X-Florence-Token": florence_access_token},
                    params=upload_params,
                    files=file,
                    verify=True,
                )
                # TODO Replace print statements with logging
                print(f"File chunk {chunk_number} of {len(file_chunks)} posted")
                chunk_number += 1

        s3_key = upload_params["resumableIdentifier"]
        s3_uri = f"s3://{s3_bucket}/{s3_key}"

        # Delete temporary files
        _delete_temp_chunks(file_chunks)
        # TODO Replace print statements with logging
        print("Upload to s3 complete")

        return s3_key, s3_uri

    def upload_new(
        self,
        csv_path: Union[Path, str],
        florence_access_token: str,
        s3_bucket: str,
        collection_id: str,
        title: str,
        is_publishable: bool = False,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload files to the DP Upload Service `upload-new` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        The `s3_bucket` and `florence_access_token` arguments should be set as environment variables and accessed via os.getenv() or similar.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        # Create file chunks
        file_chunks = _create_temp_chunks(csv_path=csv_path, chunk_size=chunk_size)

        # Generate upload request params
        upload_params = _generate_upload_new_params(
            csv_path=csv_path,
            s3_path=f"s3://{s3_bucket}",
            collection_id=collection_id,
            title=title,
            is_publishable=is_publishable,
        )

        chunk_number = 1

        for file_chunk in file_chunks:
            with open(file_chunk, "rb") as f:
                # Load file chunk as binary data
                file = {"file": f}

                # Add chunk number to upload request params
                upload_params["resumableChunkNumber"] = chunk_number

                # Submit `POST` request to `self.upload_url`
                self.post(
                    url=self.upload_url,
                    headers={"X-Florence-Token": florence_access_token},
                    params=upload_params,
                    files=file,
                    verify=True,
                )
                # TODO Replace print statements with logging
                print(f"File chunk {chunk_number} of {len(file_chunks)} posted")
                chunk_number += 1

        s3_key = upload_params["resumableIdentifier"]
        s3_uri = f"s3://{s3_bucket}/{s3_key}"

        # Delete temporary files
        _delete_temp_chunks(file_chunks)
        # TODO Replace print statements with logging
        print("Upload to s3 complete")

        return s3_key, s3_uri


def _generate_upload_params(csv_path: Union[Path, str], chunk_size: int) -> dict:
    """
    Generate request parameters that do not change when iterating through the list of file chunks.

    To be used with the `upload` endpoint.
    """
    # Get total size of file to be uploaded
    total_size = os.path.getsize(csv_path)

    # Convert csv_path string to Path
    if not isinstance(csv_path, Path):
        csv_path = Path(csv_path).absolute()

    # Get filename from csv filepath
    filename = str(csv_path).split("/")[-1]

    # Get timestamp to create `resumableIdentifier` value in `POST` params
    timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")

    # Generate upload request params
    upload_params = {
        "resumableTotalChunks": ceil(total_size / chunk_size),
        "resumableChunkSize": chunk_size,
        "resumableTotalSize": total_size,
        "resumableType": "text/csv",
        "resumableIdentifier": f"{timestamp}-{filename.replace('.', '-')}",
        "resumableFilename": filename,
    }
    return upload_params


def _generate_upload_new_params(
    csv_path: Union[Path, str],
    s3_path: str,
    collection_id: str,
    title: str,
    is_publishable: bool,
) -> dict:
    """
    Generate request parameters that do not change when iterating through the list of file chunks.

    To be used with the `upload-new` endpoint.
    """
    # Get total size of file to be uploaded
    total_size = os.path.getsize(csv_path)

    # Convert csv_path string to Path
    if not isinstance(csv_path, Path):
        csv_path = Path(csv_path).absolute()

    # Get filename from csv filepath
    filename = str(csv_path).split("/")[-1]

    # Get timestamp to create `resumableFilename` value in `upload_params`
    timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")

    # Generate upload request params
    upload_params = {
        "resumableFilename": f"{timestamp}-{filename.replace('.', '-')}",
        "path": s3_path,
        "isPublishable": is_publishable,
        "collectionId": collection_id,
        "title": title,
        "resumableTotalSize": total_size,
        "resumableType": "text/csv",
        "licence": "Open Government Licence v3.0",
        "licenceUrl": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "resumableTotalChunks": ceil(total_size / 5242880),
    }
    return upload_params


def _create_temp_chunks(
    csv_path: Union[Path, str],
    chunk_size: int = 5242880,
) -> list[str]:
    """
    Chunks up the data into text files, saves them to a temporary directory and returns list of temp filenames
    """
    chunk_number = 1
    temp_file_paths_list = []
    # Convert csv_path string to Path
    if not isinstance(csv_path, Path):
        csv_path = Path(csv_path).absolute()

    # Create TemporaryDirectory to store temporary file chunks
    with TemporaryDirectory() as output_path:
        with open(csv_path, "rb") as f:
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
