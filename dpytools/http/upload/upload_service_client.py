import os
from pathlib import Path
from typing import Optional, Union

from requests import Response

from dpytools.http.upload.base_upload import BaseUploadClient
from dpytools.http.upload.utils import (
    _create_temp_chunks,
    _delete_temp_chunks,
    _generate_upload_new_params,
    _generate_upload_params,
)
from dpytools.logging.logger import DpLogger

# Dev note:

# At time of writing (17/5/2024) there are two endpoints supported
# by the Upload Service:
# 1. /upload
# 2. /upload-new

# Putting aside the wisdom of "upload-new" we do need to support both of
# these options so have by necessity adopted this nomenclature.

logger = DpLogger("dpytools")


class UploadServiceClient(BaseUploadClient):
    def __init__(self, upload_url: str, backoff_max=30):
        super().__init__(upload_url=upload_url, backoff_max=backoff_max)

    def upload(
        self, file_path: Union[Path, str], mimetype: str, chunk_size: int = 5242880
    ) -> Response:
        """
        Upload files to the DP Upload Service `/upload` endpoint. A file of type `mimetype` (located at `file_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.
        """
        # Convert file_path string to Path
        if isinstance(file_path, str):
            file_path = Path(file_path).absolute()

        # Create file chunks
        file_chunks = _create_temp_chunks(file_path, chunk_size)
        logger.info("File chunks created", data={"file_chunks": file_chunks})
        # Generate upload request params
        upload_params = _generate_upload_params(file_path, mimetype, chunk_size)
        logger.info(
            "Upload parameters generated", data={"upload_params": upload_params}
        )
        # Upload file chunks to S3
        self._upload_file_chunks(file_chunks, upload_params)

        # Delete temporary files
        _delete_temp_chunks(file_chunks)
        logger.info(
            "Upload to s3 complete",
            data={
                "s3_key": upload_params["resumableIdentifier"],
            },
        )

    def upload_new(
        self,
        file_path: Union[Path, str],
        mimetype: str,
        chunk_size: Optional[int] = 5242880,
        alias_name: Optional[str] = None,
        title: Optional[str] = None,
        is_publishable: Optional[bool] = None,
        license: Optional[str] = None,
        license_url: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> Response:
        """
        Upload files to the DP Upload Service `upload-new` endpoint. The file to be uploaded (located at `file_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket. The file type should be specified as `mimetype` (e.g. "text/csv" for a CSV file). The remainder of the optional arguments are required for the request to the `/upload-new` endpoint to succeed. If these are not specified, defaults are set in the `_generate_upload_new_params` function call.
        """
        # Convert file_path string to Path
        if isinstance(file_path, str):
            file_path = Path(file_path).absolute()

        # Create file chunks
        file_chunks = _create_temp_chunks(file_path, chunk_size)
        logger.info("File chunks created", data={"file_chunks": file_chunks})

        # Generate upload request params
        upload_params = _generate_upload_new_params(
            file_path,
            mimetype,
            chunk_size,
            alias_name,
            title,
            is_publishable,
            license,
            license_url,
            collection_id,
        )
        logger.info(
            "Upload parameters generated", data={"upload_params": upload_params}
        )

        # Upload file chunks to S3
        response = self._upload_file_chunks(file_chunks, upload_params)

        # Delete temporary files
        _delete_temp_chunks(file_chunks)
        logger.info("Upload to s3 complete", data={"s3_key": upload_params["Path"]})
        return response

    def _upload_file_chunks(
        self,
        file_chunks: list[str],
        upload_params: dict,
    ) -> Response:
        """
        Upload file chunks to DP Upload Service with the specified upload parameters.
        """
        chunk_number = 1
        for file_chunk in file_chunks:
            current_chunk_size = os.path.getsize(Path(file_chunk))
            with open(file_chunk, "rb") as f:
                # Load file chunk as binary data
                file = {"file": f}

                # Add chunk number and current chunk size to upload request params
                upload_params["resumableChunkNumber"] = chunk_number
                upload_params["resumableCurrentChunkSize"] = current_chunk_size

                # Submit `POST` request to `self.upload_url`
                response = self.post(
                    self.upload_url,
                    headers=self.token_auth.get_auth_header(),
                    params=upload_params,
                    files=file,
                    verify=True,
                )
                logger.info(
                    "File chunk posted",
                    data={
                        "chunk_number": chunk_number,
                        "total_chunks": len(file_chunks),
                    },
                )
                chunk_number += 1
        # The HTTP response code is 200 for each chunk until the final one, which is 201. Only return the final code here.
        return response
