import os
from datetime import datetime, timedelta
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional, Union

from dpytools.http.base import BaseHttpClient
from dpytools.logging.logger import DpLogger

logger = DpLogger("dpytools")
base_http_client = BaseHttpClient()

# Dev note:

# At time of writing (17/5/2024) there's two endpoints supported
# by the uplaod service.

# 1. /upload
# 2. /upload-new

# Putting aside the wisdom of "new" we do need to support both of
# these options so have ny neceessity adopted this nomanclature.


class UploadServiceClient(BaseHttpClient):
    def __init__(self, upload_url: str, backoff_max=30):
        super().__init__(backoff_max=backoff_max)
        self.upload_url = upload_url
        # RE auth, there'd two modes
        # 1. Service account mode
        # 2. User account mode
        # The headers used are slightly different and
        # user account mode required refreshing the auth
        # token before a 15 minute timeout happens
        # (service account auth doesn't time out)

        self.service_token = os.environ.get("SERVICE_TOKEN_FOR_UPLOAD")
        if self.service_token is None:
            self.set_user_tokens()

    def set_user_tokens(self):
        """
        When using user auth we need to use florence username and password
        to create a florence token.

        We also need to get the refresh token so we can extend the token
        lifespan beyond the 15 minute timeout where necessary.
        """

        self.florence_user = os.environ.get("FLORENCE_USER", None)
        self.florence_password = os.environ.get("FLORENCE_PASSWORD", None)
        self.identity_api_url = os.environ.get("IDENTITY_API_URL", None)

        assert (
            self.florence_user is not None
        ), "Where env var SERVICE_TOKEN_FOR_UPLOAD is None, env var FLORENCE_USER must be provided"
        assert (
            self.florence_user is not None
        ), "Where env var SERVICE_TOKEN_FOR_UPLOAD is None, env var FLORENCE_PASSOWRD must be provided"
        assert (
            self.florence_user is not None
        ), "Where env var SERVICE_TOKEN_FOR_UPLOAD is None, env var IDENTITY_API_URL must be provided"

        # https://github.com/ONSdigital/dp-identity-api/blob/develop/swagger.yaml
        token_url = f"{self.identity_api_url}/tokens"
        response = self.post(
            token_url,
            json={"login": self.florence_user, "password": self.florence_password},
        )
        if response.status_code == 201:
            response_headers = response.headers

            self.refresh_token = response_headers["Refresh"]
            self.token_creation_time = datetime.now()

            self.auth_token = response_headers["Authorization"]
            self.id_token = response_headers["ID"]
        else:
            err = Exception("Failed to create user tokens")
            logger.error(
                "Failed to create user tokens",
                err,
                data={
                    "identity_api_url": self.identity_api_url,
                    "token_url": token_url,
                    "response_staus_code": response.status_code,
                    "response_content": response.content,
                },
            )
            raise err

    def get_auth_header(self) -> Dict[str, str]:
        """
        Given a dictionary of params, set the auth header based on the
        auth mode in use.
        """

        # Using service account
        if self.service_token:
            return {"Authorization": f"Bearer {self.service_token}"}

        # Using user account
        # If the token is more than 10 minutes old refresh it
        # https://github.com/ONSdigital/dp-identity-api/blob/develop/swagger.yaml
        if (datetime.now() - self.token_creation_time) > timedelta(minutes=10):
            token_refresh_url = f"{self.identity_api_url}/tokens/self"
            response = self.put(
                token_refresh_url,
                json={"Refresh": self.refresh_token, "ID": self.id_token},
            )

        if response.status_code == 201:
            self.auth_token = response.headers["Authorization"]
            self.id_token = response.headers["ID"]
        else:
            err = Exception(
                f"Refreshing token failed, returned a {response.status_code} error"
            )
            logger.error(
                "Could not refresh user auth token",
                err,
                data={
                    "token_refresh_url": token_refresh_url,
                    "response_status_code": response.status_code,
                    "response_content": response.content,
                },
            )
            raise err

        return {"X-Florence-Token": self.auth_token, "ID": self.id_token}

    def upload_csv(
        self,
        csv_path: Union[Path, str],
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload csv files to the DP Upload Service `/upload` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.
        """
        self._upload(csv_path, "text/csv", chunk_size)

    def upload_sdmx(
        self,
        sdmx_path: Union[Path, str],
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload sdmx files to the DP Upload Service `/upload` endpoint. The file to be uploaded (located at `sdmx_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.
        """
        self._upload(sdmx_path, "application/xml", chunk_size)

    def upload_new_csv(
        self,
        csv_path: Union[Path, str],
        alias_name: Optional[str] = None,
        title: Optional[str] = None,
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload csv files to the DP Upload Service `/upload-new` endpoint. The file to be uploaded (located at `csv_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        `alias_name` and `title` are optional arguments. If these are not explicitly provided, `alias_name` will default to the filename with the extension, and `title` will default to the filename without the extension - e.g. if the filename is "data.csv", `alias_name` defaults to "data.csv" and `title` defaults to "data".
        """
        self._upload_new(
            csv_path,
            "text/csv",
            alias_name,
            title,
            chunk_size,
        )

    def upload_new_sdmx(
        self,
        sdmx_path: Union[Path, str],
        alias_name: Optional[str] = None,
        title: Optional[str] = None,
        chunk_size: int = 5242880,
    ) -> None:
        """
        Upload sdmx files to the DP Upload Service `/upload-new` endpoint. The file to be uploaded (located at `sdmx_path`) is chunked (default chunk size 5242880 bytes) and uploaded to an S3 bucket.

        `alias_name` and `title` are optional arguments. If these are not explicitly provided, `alias_name` will default to the filename with the extension, and `title` will default to the filename without the extension - e.g. if the filename is "data.csv", `alias_name` defaults to "data.csv" and `title` defaults to "data".
        """
        self._upload_new(
            sdmx_path,
            "application/xml",
            alias_name,
            title,
            chunk_size,
        )

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
        self._upload_file_chunks(file_chunks, upload_params
                                 )

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
                    headers=self.get_auth_header(),
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
    timestamp = datetime.now().strftime("%d%m%y%H%M%S")

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
    chunk_size: int,
    mimetype: str,
    alias_name: Optional[str],
    title: Optional[str],
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

    # Get timestamp to create `resumableIdentifier` value in `upload_params`
    timestamp = datetime.now().strftime("%d%m%y%H%M%S")

    # Create identifier from timestamp and filename
    identifier = f"{timestamp}-{filename.replace('.', '-')}"

    if alias_name is None:
        alias_name = filename

    if title is None:
        title = filename.split(".")[0]

    # Generate upload request params
    upload_params = {
        "resumableTotalChunks": ceil(total_size / 5242880),
        "resumableChunkSize": chunk_size,
        "resumableTotalSize": total_size,
        "resumableType": mimetype,
        "resumableIdentifier": identifier,
        "resumableFilename": filename,
        "resumableRelativePath": str(file_path),
        "aliasName": alias_name,
        # TODO Currently the POST request in `_upload_file_chunks` is failing due to an potential issue with the Go code (HTTP 500 error: `bad request: unknown error: : duplicate file path`)
        # Once the Go issue is resolved, check that the Path is in the correct format
        # See https://github.com/ONSdigital/dp-api-clients-go/blob/a26491512a8336ad9c31b694c045d8e3a3ed0578/files/client.go#L160
        "Path": f"datasets/{identifier}",
        "isPublishable": is_publishable,
        "Title": title,
        # `SizeInBytes` may be populated from `resumableTotalSize` - check once `Path` issue has been resolved
        "SizeInBytes": total_size,
        # `Type` may be populated from `resumableType` - check once `Path` issue has been resolved
        "Type": mimetype,
        "Licence": licence,
        "LicenceUrl": licence_url,
        # `CollectionID`, `State` and `Etag` fields omitted as not required
    }
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
