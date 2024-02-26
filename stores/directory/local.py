from __future__ import annotations

from abc import ABC, abstractmethod, abstractstaticmethod
import json
from pathlib import Path
from typing import List, Optional, Union
import re

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

        # check that exactly 1 file name match the regex pattern, 0 files match or more than 1 file matches.
        if not matching_files.count == 1:
            return True
        elif matching_files.count < 1:
            raise ValueError("No files matching regex patten found")
        elif matching_files.count > 1:
            raise ValueError(
                "More than one file found that matches the regex pattern")

    def save_lone_file_matching(self, pattern: str, destination: Optional[Union[Path, str]] = None):
        """
        Asserts there's exactly one file in the directory matching the provided regex

        If no destination is provided, save it in the current working directory with
        its current filename.

        If a destination is provided, if that destination is a str, change to to a python
        pathlib.Path object then save it there.

        In both cases raise an exception if a file with that name already exists where
        we've been asked to save a new one.
        """
        if self.has_lone_file_matching(pattern):

            if not destination:
                open(pattern, "x")

            else:
                if isinstance(destination, str):
                    full_path = destination + "/" + pattern
                    save_path = Path(full_path)
                    assert not save_path.is_file(), "Given file already exists in directory."
                    with (save_path / pattern).open("w") as saved_pattern:
                        pass
                else:
                    save_path = destination / pattern
                    assert not save_path.is_file(), "Given file already exists in directory."
                    with (destination / pattern).open("w") as saved_pattern:
                        pass

    def get_lone_matching_json_as_dict(self, pattern: str, pattern_directory: Union[Path, str]) -> dict:
        """"
        Asserts exactly 1 file matches pattern.
        Raise if someone doesent end their pattern with .json?
        Return the contents of the matching json as a dictionary.
        """

        if self.has_lone_file_matching(pattern):
            assert pattern.endswith(".json"), "File doesn't end with .json"
            if isinstance(pattern_directory, str):
                str_path = pattern_directory + "/" + pattern
                full_path = Path(str_path)
                assert full_path.isfile(), "Given path to pattern does not exist."
            else:
                full_path = pattern_directory / pattern
                assert full_path.isfile(), "Given path to pattern does not exist."

            # use json.load to put contents of file into variable and return dic.
            pattern_dict = json.load(full_path)
            return pattern_dict

    def save_lone_file_matching_regex(self, regex_str) -> Path:
        # Abstract methods can remain without implementation for now.
        ...

    def get_file_names(self) -> List[str]:
        # Abstract methods can remain without implementation for now.
        ...

    def get_current_source_pathlike(self) -> str:
        # Abstract methods can remain without implementation for now.
        ...
