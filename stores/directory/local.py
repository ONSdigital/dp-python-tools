from __future__ import annotations

from abc import ABC, abstractmethod, abstractstaticmethod
from pathlib import Path
from typing import List

from stores.directory.base import BaseWritableSingleDirectoryStore


class LocalDirectoryStore(BaseWritableSingleDirectoryStore):

    local_path: Path

    def __init__(self, local_dir):
        # Takes a path or a string representing a path as input

        # If it is not a path, pathify it
        if type(local_dir) != Path:
            try:
                local_dir = Path(local_dir)
            except:
                raise TypeError(f"Given path {local_dir} is not a path and cannot be converted to a path.")

        # Make sure it exists
        assert local_dir.exists(), "Given path does not exist as a local directory."

        # Store that location against the class

        self.local_path = local_dir


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








