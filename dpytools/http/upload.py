import datetime
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
        # For security purposes, `self.access_token` should be set using a FLORENCE_TOKEN environment variable
        self.access_token = os.environ.get("FLORENCE_TOKEN")
        self.headers = {"X-Florence-Token": self.access_token}

    # TODO The `upload` method is currently configured to match the old `upload` endpoint specification. Once the `upload-new` endpoint has been released, the `params` argument passed to `self.post` will need to be adjusted to the new specification (see https://github.com/ONSdigital/dp-upload-service/blob/b91b53a13b28c6ba1095abee71680c591862c68c/swagger.yaml).
    def upload(
        self,
        csv_path: Union[Path, str],
        s3_path: str,
        chunk_size: int = 5242880,
    ) -> Tuple[str, str]:
        """
        Upload files to the DP Upload Service. Files (located at `csv_path`) are chunked (default chunk size 5242880 bytes) and uploaded to the S3 bucket located at `s3_path`.

        Returns the S3 Object key and full S3 URL of the uploaded file.
        """
        # Get total size of file to be uploaded
        total_size = str(os.path.getsize(csv_path))

        # Convert csv_path string to Path
        if not isinstance(csv_path, Path):
            csv_path = Path(csv_path).absolute()

        # Get filename from csv filepath
        filename = str(csv_path).split("/")[-1]

        # Get timestamp to create `resumableIdentifier` value in `POST` params
        timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")

        # Create file chunks
        file_chunks = self._create_temp_chunks(csv_path=csv_path, chunk_size=chunk_size)

        chunk_number = 1

        for file_chunk in file_chunks:
            with open(file_chunk, "rb") as f:
                # Load file chunk as binary data
                file = {"file": f}

                # TODO current_chunk_size = len(f.read()) is causing the request to fail?
                # current_chunk_size = len(f.read())

                # Construct `POST` request params for each file chunk
                params = {
                    "resumableChunkNumber": chunk_number,
                    "resumableTotalChunks": len(file_chunks),
                    "resumableChunkSize": chunk_size,
                    # TODO See comment above re current_chunk_size
                    # "resumableCurrentChunkSize": current_chunk_size,
                    "resumableTotalSize": total_size,
                    "resumableType": "text/csv",
                    "resumableIdentifier": f"{timestamp}-{filename.replace('.', '-')}",
                    "resumableFilename": filename,
                    # TODO resumableRelativePath and aliasName values
                    # "resumableRelativePath": "",
                    # "aliasName": "",
                }

                # Submit `POST` request to `self.upload_url`
                self.post(
                    url=self.upload_url,
                    headers=self.headers,
                    params=params,
                    files=file,
                    verify=True,
                )
                # TODO Replace print statements with logging
                print(f"File chunk {chunk_number} of {len(file_chunks)} posted")
                chunk_number += 1

        s3_key = params["resumableIdentifier"]
        s3_url = f"{s3_path}/{s3_key}"

        # Delete temporary files
        self._delete_temp_chunks(file_chunks)
        # TODO Replace print statements with logging
        print("Upload to s3 complete")

        return s3_key, s3_url

    def _create_temp_chunks(
        self,
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
                    # Write chunk to temporary filepath
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(chunk)
                        temp_file_paths_list.append(temp_file_path)
                    chunk_number += 1
                    chunk = f.read(chunk_size)
        # Return list of temporary filepaths
        return temp_file_paths_list

    def _delete_temp_chunks(self, temp_file_paths_list: list):
        """
        Deletes the temporary chunks that were uploaded
        """
        for file in temp_file_paths_list:
            os.remove(file)
