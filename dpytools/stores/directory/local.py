from __future__ import annotations

from abc import ABC, abstractmethod, abstractstaticmethod
from pathlib import Path
from typing import List, Union

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

        # Store that location against the class

        self.local_path = local_dir_path

    def add_file(self, file: Path):
        # Abstract methods can remain without implementation for now.
        pass

    def has_lone_file_matching(self, pattern: str) -> bool:
        #  To be implemented in local directory store 1 #5
        ...

    def save_lone_file_matching(self, pattern: str, save_as: str) -> Path:
        #  To be implemented in local directory store 1 #5
        ...

    def get_lone_matching_json_as_dict(self, pattern: str) -> dict:
        #  To be implemented in local directory store 1 #5
        ...

    def save_lone_file_matching_regex(self, regex_str) -> Path:
        # Abstract methods can remain without implementation for now.
        ...

    def get_file_names(self) -> List[str]:
        # Abstract methods can remain without implementation for now.
        ...

    def get_current_source_pathlike(self) -> str:
        # Abstract methods can remain without implementation for now.
        ...
