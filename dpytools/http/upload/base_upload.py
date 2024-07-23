import os
from pathlib import Path
from typing import Optional, Union

from dpytools.http.base import BaseHttpClient
from dpytools.logging.logger import DpLogger

from ..token_auth import TokenAuth
from .utils import (
    _create_temp_chunks,
    _delete_temp_chunks,
    _generate_upload_new_params,
    _generate_upload_params,
)

logger = DpLogger("dpytools")


class BaseUploadClient(BaseHttpClient):
    def __init__(self, upload_url: str, backoff_max=30):
        super().__init__(backoff_max=backoff_max)
        self.token_auth = TokenAuth(backoff_max=backoff_max)
        self.upload_url = upload_url

    def _upload(
        self,
        file_path: Union[Path, str],
        mimetype: str,
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload files to the DP Upload Service `/upload` endpoint. The file to be uploaded (located at `file_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket. The file type should be specified as `mimetype` (e.g. "text/csv" for a CSV file).
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

    def _upload_new(
        self,
        file_path: Union[Path, str],
        mimetype: str,
        alias_name: Optional[str],
        title: Optional[str],
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload files to the DP Upload Service `upload-new` endpoint. The file to be uploaded (located at `file_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket. The file type should be specified as `mimetype` (e.g. "text/csv" for a CSV file).
        """
        # Convert file_path string to Path
        if isinstance(file_path, str):
            file_path = Path(file_path).absolute()

        # Create file chunks
        file_chunks = _create_temp_chunks(file_path, chunk_size)
        logger.info("File chunks created", data={"file_chunks": file_chunks})

        # Generate upload request params
        upload_params = _generate_upload_new_params(
            file_path, chunk_size, mimetype, alias_name, title
        )
        logger.info(
            "Upload parameters generated", data={"upload_params": upload_params}
        )

        # Upload file chunks to S3
        self._upload_file_chunks(file_chunks, upload_params)

        # Delete temporary files
        _delete_temp_chunks(file_chunks)
        logger.info("Upload to s3 complete", data={"s3_key": upload_params["Path"]})

    def _upload_file_chunks(
        self,
        file_chunks: list[str],
        upload_params: dict,
    ) -> None:
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
                self.post(
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
