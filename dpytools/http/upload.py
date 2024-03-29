import datetime
from math import ceil
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Tuple, Union

from dpytools.http.base import BaseHttpClient


class UploadClient(BaseHttpClient):
    def __init__(self, upload_url: str):
        # Inherit backoff_max value from BaseHTTPClient.__init__
        super().__init__()
        self.upload_url = upload_url

    def upload_csv(
        self,
        csv_path: Union[Path, str],
        s3_bucket: str,
        florence_access_token: str,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload csv files to the DP Upload Service `upload` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        The `s3_bucket` argument should be set as an environment variable and accessed via os.getenv() or similar. `florence_access_token` should be generated via the DP Identity API and passed as a string argument.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        self._upload(csv_path, s3_bucket, florence_access_token, "text/csv", chunk_size)

    def upload_sdmx(
        self,
        sdmx_path: Union[Path, str],
        s3_bucket: str,
        florence_access_token: str,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload sdmx files to the DP Upload Service `upload` endpoint. The file to be uploaded (located at `sdmx_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        The `s3_bucket` argument should be set as an environment variable and accessed via os.getenv() or similar. `florence_access_token` should be generated via the DP Identity API and passed as a string argument.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        self._upload(
            sdmx_path, s3_bucket, florence_access_token, "application/xml", chunk_size
        )

    def upload_new_csv(
        self,
        csv_path: Union[Path, str],
        florence_access_token: str,
        s3_bucket: str,
        title: str,
        collection_id: Optional[str],
        is_publishable: bool = False,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload csv files to the DP Upload Service `upload-new` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        The `s3_bucket` argument should be set as an environment variable and accessed via os.getenv() or similar. `florence_access_token` should be generated via the DP Identity API and passed as a string argument.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        self._upload_new(
            csv_path,
            s3_bucket,
            florence_access_token,
            title,
            "text/csv",
            collection_id,
            is_publishable,
            chunk_size,
        )

    def upload_new_sdmx(
        self,
        sdmx_path: Union[Path, str],
        florence_access_token: str,
        s3_bucket: str,
        title: str,
        collection_id: Optional[str],
        is_publishable: bool = False,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload sdmx files to the DP Upload Service `upload-new` endpoint. The file to be uploaded (located at `sdmx_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        The `s3_bucket` argument should be set as an environment variable and accessed via os.getenv() or similar. `florence_access_token` should be generated via the DP Identity API and passed as a string argument.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        self._upload_new(
            sdmx_path,
            s3_bucket,
            florence_access_token,
            title,
            "application/xml",
            collection_id,
            is_publishable,
            chunk_size,
        )

    def _upload(
        self,
        file_path: Union[Path, str],
        s3_bucket: str,
        florence_access_token: str,
        mimetype: str,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload files to the DP Upload Service `upload` endpoint. The file to be uploaded (located at `file_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket. The file type should be specified as `mimetype`.

        The `s3_bucket` argument should be set as an environment variable and accessed via os.getenv() or similar. `florence_access_token` should be generated via the DP Identity API and passed as a string argument.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        # Convert file_path string to Path
        if isinstance(file_path, str):
            file_path = Path(file_path).absolute()

        # Create file chunks
        file_chunks = _create_temp_chunks(file_path, chunk_size)

        # Generate upload request params
        upload_params = _generate_upload_params(file_path, mimetype, chunk_size)

        # Upload file chunks to S3
        self._upload_file_chunks(file_chunks, upload_params, florence_access_token)

        s3_key = upload_params["resumableIdentifier"]
        s3_uri = f"s3://{s3_bucket}/{s3_key}"

        # Delete temporary files
        _delete_temp_chunks(file_chunks)

        # TODO Replace print statements with logging
        print("Upload to s3 complete")

        return s3_key, s3_uri

    def _upload_new(
        self,
        file_path: Union[Path, str],
        s3_bucket: str,
        florence_access_token: str,
        title: str,
        mimetype: str,
        collection_id: Optional[str],
        is_publishable: bool = False,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload files to the DP Upload Service `upload-new` endpoint. The file to be uploaded (located at `file_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket. The file type should be specified as `mimetype`.

        The `s3_bucket` argument should be set as an environment variable and accessed via os.getenv() or similar. `florence_access_token` should be generated via the DP Identity API and passed as a string argument.

        Returns the S3 Object key and S3 URL of the uploaded file.
        """
        # Convert file_path string to Path
        if isinstance(file_path, str):
            file_path = Path(file_path).absolute()

        # Create file chunks
        file_chunks = _create_temp_chunks(file_path, chunk_size)

        # Generate upload request params
        upload_params = _generate_upload_new_params(
            file_path,
            f"s3://{s3_bucket}",
            title,
            mimetype,
            collection_id,
            is_publishable,
        )

        # Upload file chunks to S3
        self._upload_file_chunks(file_chunks, upload_params, florence_access_token)

        s3_key = upload_params["resumableFilename"]
        s3_uri = f"s3://{s3_bucket}/{s3_key}"

        # Delete temporary files
        _delete_temp_chunks(file_chunks)

        # TODO Replace print statements with logging
        print("Upload to s3 complete")

        return s3_key, s3_uri

    def _upload_file_chunks(
        self, file_chunks: list[str], upload_params: dict, florence_access_token: str
    ) -> None:
        """
        Upload file chunks to DP Upload Service with the specified upload parameters.
        """
        chunk_number = 1
        for file_chunk in file_chunks:
            with open(file_chunk, "rb") as f:
                # Load file chunk as binary data
                file = {"file": f}

                # Add chunk number to upload request params
                upload_params["resumableChunkNumber"] = chunk_number

                # Submit `POST` request to `self.upload_url`
                self.post(
                    self.upload_url,
                    headers={"X-Florence-Token": florence_access_token},
                    params=upload_params,
                    files=file,
                    verify=True,
                )
                # TODO Replace print statements with logging
                print(f"File chunk {chunk_number} of {len(file_chunks)} posted")
                chunk_number += 1


def _generate_upload_params(file_path: Path, mimetype: str, chunk_size: int) -> dict:
    """
    Generate request parameters that do not change when iterating through the list of file chunks.

    To be used with the `upload` endpoint.
    """
    # Get total size of file to be uploaded
    total_size = os.path.getsize(file_path)

    # Get filename from csv filepath
    filename = str(file_path).split("/")[-1]

    # Get timestamp to create `resumableIdentifier` value in `POST` params
    timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")

    # Generate upload request params
    upload_params = {
        "resumableTotalChunks": ceil(total_size / chunk_size),
        "resumableChunkSize": chunk_size,
        "resumableTotalSize": total_size,
        "resumableType": mimetype,
        "resumableIdentifier": f"{timestamp}-{filename.replace('.', '-')}",
        "resumableFilename": filename,
    }
    return upload_params


def _generate_upload_new_params(
    file_path: Path,
    s3_path: str,
    title: str,
    mimetype: str,
    collection_id: Optional[str],
    is_publishable: bool = False,
    licence: str = "Open Government Licence v3.0",
    licence_url: str = "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
) -> dict:
    """
    Generate request parameters that do not change when iterating through the list of file chunks.

    To be used with the `upload-new` endpoint.
    """
    # Get total size of file to be uploaded
    total_size = os.path.getsize(file_path)

    # Get filename from csv filepath
    filename = str(file_path).split("/")[-1]

    # Get timestamp to create `resumableFilename` value in `upload_params`
    timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")

    # Generate upload request params
    upload_params = {
        "resumableFilename": f"{timestamp}-{filename.replace('.', '-')}",
        "path": s3_path,
        "isPublishable": is_publishable,
        "title": title,
        "resumableTotalSize": total_size,
        "resumableType": mimetype,
        "licence": licence,
        "licenceUrl": licence_url,
        "resumableTotalChunks": ceil(total_size / 5242880),
    }

    if collection_id is not None:
        upload_params["collectionId"] = collection_id

    return upload_params


def _create_temp_chunks(
    csv_path: Path,
    chunk_size: int = 5242880,
) -> list[str]:
    """
    Chunks up the data into text files, saves them to a temporary directory and returns list of temp filenames
    """
    chunk_number = 1
    temp_file_paths_list = []

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
