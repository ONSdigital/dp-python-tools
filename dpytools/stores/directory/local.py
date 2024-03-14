from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import List, Optional, Union

from dpytools.stores.directory.base import BaseWritableSingleDirectoryStore


class LocalDirectoryStore(BaseWritableSingleDirectoryStore):
    def __init__(self, local_dir: Union[str, Path]):
        # Takes a path or a string representing a path as input

        # If it is not a path, pathify it
        if not isinstance(local_dir, Path):
            local_dir_path = Path(local_dir)
        else:
            local_dir_path = local_dir

        # Make sure it exists and it's a directory.
        assert local_dir_path.exists(), f"Given path {local_dir_path} does not exist."
        assert (
            local_dir_path.is_dir()
        ), f"Given path {local_dir_path} is not a directory."
        assert (
            local_dir_path.is_dir()
        ), f"Given path {local_dir_path} is not a directory."

        # Store that location against the class

        self.local_path = local_dir_path

    def add_file(self, file_name: Union[str, Path]) -> Path:
        """
        Add file to local directory store
        """
        # Convert file to pathlib.Path
        if not isinstance(file_name, Path):
            file_name = Path(file_name)

        # Check the file exists
        assert file_name.exists(), f"Given file {file_name} does not exist."

        # Create local file path
        local_file_path = Path(os.path.join(self.local_path, file_name.name))

        # Read file and write to local path
        with open(file_name, "rb") as f:
            file_content = f.read()
        with open(local_file_path, "wb") as fp:
            fp.write(file_content)
        return local_file_path

    def add_file(self, file_name: Union[str, Path]) -> Path:
        """
        Add file to local directory store
        """
        # Convert file to pathlib.Path
        if not isinstance(file_name, Path):
            file_name = Path(file_name)

        # Check the file exists
        assert file_name.exists(), f"Given file {file_name} does not exist."

        # Create local file path
        local_file_path = Path(os.path.join(self.local_path, file_name.name))

        # Read file and write to local path
        with open(file_name, "rb") as f:
            file_content = f.read()
        with open(local_file_path, "wb") as fp:
            fp.write(file_content)
        return local_file_path

    def has_lone_file_matching(self, pattern: str) -> bool:
        # Grab a list of files matching the regex pattern to determine how many exist.

        matching_files = self._files_that_match_pattern(pattern)

        if len(matching_files) == 1:  # 1 file matched
            return True
        elif len(matching_files) == 0:  # 0 file matched
            return False
        else:  # 2+ files matched
            raise FileNotFoundError(
                f"More than 1 file found that matches the regex pattern '{pattern}' in directory {self.local_path}. Matching: {matching_files}"
            )

    def save_lone_file_matching(
        self, pattern: str, destination: Optional[Union[Path, str]] = None
    ):
        """
        Asserts a file matches the given pattern, then saves it to the given destination.
        """
        # Assert 1 file matches
        if not self.has_lone_file_matching(pattern):
            raise FileNotFoundError(
                f"No matching files found for pattern {pattern} in directory {self.local_path}"
            )

        file_to_save = self._files_that_match_pattern(pattern)[0]
        file_name = Path(file_to_save).name

        # If a destination is given, save the matched file there.
        if destination is not None:
            if isinstance(destination, str):
                destination = Path(destination)
            assert (
                destination.exists()
            ), f"Destination directory {destination} does not exist."
            save_path = Path(destination / file_name)
        # If no destination is given, save the matched file in the current directory.
        else:
            save_path = Path(file_name)

        # If the file already exists in the save directory, raise an error.
        if save_path.exists():
            raise ValueError(f"Given file already exists in directory {save_path}")

        file_path_to_save = self.local_path / file_to_save
        with open(file_path_to_save) as f:
            file_data = f.read()

        with open(save_path, "w") as f:
            f.write(file_data)

    def get_lone_matching_json_as_dict(self, pattern: str) -> dict:
        # Assert 1 file matches
        if self.has_lone_file_matching(pattern):
            file_path = Path(
                self.local_path / self._files_that_match_pattern(pattern)[0]
            )

            # use json.load to put contents of file into variable and return dict.
            with open(file_path) as f:
                json_dict = json.load(f)
            return json_dict

    def get_file_names(self) -> List[str]:
        """
        Returns a list of the files in the store.
        """
        file_names = os.listdir(self.local_path)  # grab list of full paths to files,
        if len(file_names) == 0:
            return []
        else:
            return file_names

    def _files_that_match_pattern(self, pattern) -> List[str]:
        # given a pattern, return a list of all files that match it.
        # use self.get_files_names() in here as well.
        matching_files = [f for f in self.get_file_names() if re.search(pattern, f)]

        return matching_files

    def get_current_source_pathlike(self) -> str:
        """
        Returns the local path as a string
        """
        return str(self.local_path.absolute())
        """
        Returns the local path as a string
        """
        return str(self.local_path.absolute())
