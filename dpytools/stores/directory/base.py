from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union


class BaseReadableSingleDirectoryStore(ABC):
    """
    A base class for a directory like store, i.e some abstraction for organising files, examples:


    - local file system
    - amazon s3
    - google cloud storage
    - github repositories


    This class is instantiated to utlise/wrap a single "directory" and treats the contents at that (and only that) "directory" as the store.
    """

    @abstractmethod
    def has_lone_file_matching(self, pattern: str) -> bool:
        """
        Does the store have exactly 1 file name matching the regex pattern.
        """
        ...

    @abstractmethod
    def save_lone_file_matching(
        self, pattern: str, destination: Optional[Union[Path, str]] = None
    ):
        """
        Assert 1 file matches
        Save it as the provided file to current path
        Return full path to file
        """

    @abstractmethod
    def get_lone_matching_json_as_dict(self, pattern: str) -> dict:
        """
        Asserts exactly 1 file matches pattern.
        Raise if someone doesent end their pattern with .json?
        Return the contents of the matching json as a dictionary.
        """
        ...

    @abstractmethod
    def get_file_names(self) -> List[str]:
        """
        Returns the filename and extension of all files in the submission.
        """
        ...

    @abstractmethod
    def get_current_source_pathlike(self) -> str:
        """
        Get the source in terms of the current path like location as a string representing the directory/bucket-like the files are in.
        """
        ...


class BaseWritableSingleDirectoryStore(BaseReadableSingleDirectoryStore):
    """
    Extends BaseReadableSingleDirectoryStore with addititve logic which would not
    be appropriate for all directory like stores.
    """

    @abstractmethod
    def add_file(self, file_name: Union[str, Path]) -> Path:
        """
        Add a local file to the directory like store.
        """
        ...
