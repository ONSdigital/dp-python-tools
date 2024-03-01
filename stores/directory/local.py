from __future__ import annotations

from abc import ABC, abstractmethod, abstractstaticmethod
import json
from pathlib import Path
from typing import List, Optional, Union
import re
import os

from stores.directory.base import BaseWritableSingleDirectoryStore


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
        assert local_dir_path.is_dir(), f"Given path {local_dir_path} is not a directory."

        # Store that location against the class
        self.local_path = local_dir_path

    def add_file(self, file: Path):
        # Abstract methods can remain without implementation for now.
        pass

    def has_lone_file_matching(self, pattern: str) -> bool:
        # Grab a list of files matching the regex pattern to determine how many exist.

        matching_files = self._files_that_match_pattern(pattern)

        if len(matching_files) == 1:  # 1 file matched
            return True
        elif len(matching_files) == 0:  # 0 file matched
            return False         
        else:  # 2+ files matched
            raise FileNotFoundError(f"More than 1 file found that matches the regex pattern '{pattern}' in directory {self.local_path}. Matching: {matching_files}")

    def save_lone_file_matching(self, pattern: str, destination: Optional[Union[Path, str]] = None):
        # Assert 1 file matches
        if not self.has_lone_file_matching(pattern):
            raise FileNotFoundError(f"No matching files found for pattern {pattern} in directory {self.local_path}")

        file_to_save = self._files_that_match_pattern(pattern)[0]
        file_name = Path(file_to_save).name

        if destination is not None:
            if isinstance(destination, str):
                destination = Path(destination)
            
            save_path = Path(destination / file_name)
        else:
            save_path = Path(file_name)

        if save_path.exists():
            raise ValueError(f"Given file already exists in directory {save_path}")

        with open(file_to_save) as f:
            file_data = f.read()

        with open(save_path, "w") as f:
            f.write(file_data)


    def get_lone_matching_json_as_dict(self, pattern: str) -> dict:
        # Assert 1 file matches
        if self.has_lone_file_matching(pattern): 
            file_path = Path(self.local_path / self._files_that_match_pattern(pattern)[0])

            # use json.load to put contents of file into variable and return dict.
            with open(file_path) as f:
                json_dict = json.load(f)
            return json_dict

    def save_lone_file_matching_regex(self, regex_str) -> Path:
        # Abstract methods can remain without implementation for now.
        ...

    def get_file_names(self) -> List[str]:
        file_names = os.listdir(self.local_path) #grab list of full paths to files,
        #Check some files actually exist. 
        if len(file_names) < 1:
            return []
        else:
            return file_names

    def _files_that_match_pattern(self, pattern) -> List[str]:
     # given a pattern, return a list of all files that match it.
     # use self.get_files_names() in here as well.
        matching_files = [
            f for f in self.get_file_names() if re.search(pattern, f)]

        return matching_files


    def get_current_source_pathlike(self) -> str:
        # Abstract methods can remain without implementation for now.
        ...
