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
        assert local_dir_path.exists(), f"Given path {
            local_dir_path} does not exist."
        assert local_dir_path.is_dir(), f"Given path {
            local_dir_path} is not a directory."

        # Store that location against the class
        self.local_path = local_dir_path

    def add_file(self, file: Path):
        # Abstract methods can remain without implementation for now.
        pass

    def has_lone_file_matching(self, pattern: str) -> bool:
        # Grab a list of files matching the regex pattern to determin how many exist.
        matching_files = [
            f for f in self.get_file_names if re.search(pattern, f)]

        if matching_files.count == 1:  # 1 file matched
            return True
        elif matching_files.count == 0:  # 0 file matched
            return False
        elif matching_files.count > 1:  # 2+ files matched
            raise ValueError(f"More than 1 file found that matches the regex pattern in gven directory {matching_files}") 

    def save_lone_file_matching(self, pattern: str, destination: Optional[Union[Path, str]] = None):
        # Assert 1 file matches
        if self.has_lone_file_matching(pattern):
            file_name_list = self.get_file_names()
            file_name = file_name_list[0]  
            
            if not destination:
                open(file_name, "x")
            else:
                if isinstance(destination, str):
                    save_path = Path(destination)
                    assert not save_path.is_file(), "Given file already exists in directory."
                    with (save_path).open("w") as saved_pattern:
                        pass
                else:

                    assert not destination.is_file(), "Given file already exists in directory."
                    with (destination).open("w") as saved_pattern:
                        pass

    def get_lone_matching_json_as_dict(self, pattern: str) -> dict:
        # Assert 1 file matches
        if self.has_lone_file_matching(pattern): 
            file_names = self.get_file_names()
            file_name = file_names[0] 
            assert pattern.endswith(".json"), "File doesn't end with .json"
            if isinstance(file_name, str):
                file_name = Path(file_name)
                assert file_name.isfile(), "Given path to pattern does not exist."
            else:
                assert file_name.isfile(), "Given path to pattern does not exist."

            # use json.load to put contents of file into variable and return dict.
            with open(file_name) as f:
                json_dict = json.load(f)
            return json_dict

    def save_lone_file_matching_regex(self, regex_str) -> Path:
        # Abstract methods can remain without implementation for now.
        ...

    def get_file_names(self) -> List[str]:
        file_names = os.listdir(self.local_path) #grab list of full paths to files,
        #Check some files actually exist. 
        if file_names.count < 1:  # should this raise an error if empty or just fail silently and do nothing.. ?
            raise ValueError(f"No files found in given directory {file_names}")
        else:
            return file_names

    def get_current_source_pathlike(self) -> str:
        # Abstract methods can remain without implementation for now.
        ...
