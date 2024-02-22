from _pytest.monkeypatch import monkeypatch
import pytest
from pathlib import Path, PosixPath

from stores.directory.local import LocalDirectoryStore

def test_local_directory_store_path():
    """
    Ensures a LocalDirectoryStore can be instantiated from a
    given Path and that it can store the path to a correct 
    existing local directory.
    """

    test_path = Path("tests/test_local_directory.py")
    
    test_local_dir_store = LocalDirectoryStore(test_path)

    assert test_local_dir_store.local_path == PosixPath('tests/test_local_directory.py')


def test_local_directory_store_string():
    """
    Ensures a LocalDirectoryStore can be instantiated from a
    given string, and that string can be converted to a Path
    which represents a correct existing local directory.
    """

    test_path = "tests/test_local_directory.py"
    
    test_local_dir_store = LocalDirectoryStore(test_path)

    assert test_local_dir_store.local_path == PosixPath('tests/test_local_directory.py')


def test_local_directory_store_type_error():
    """
    Ensures a LocalDirectoryStore object instantiated with a
    given input type that cannot be converted to a Path raises the 
    expected TypeError.
    """

    test_path = 6

    with pytest.raises(TypeError) as err:
        test_local_dir_store = LocalDirectoryStore(test_path)

    assert "Given path 6 is not a path and cannot be converted to a path." in str(err.value)


def test_local_directory_store_non_existing():
    """
    Ensures a LocalDirectoryStore object instantiated with a
    given input that is a Path object or can be converted to a
    Path raises the expected error if the path does not exist locally.
    """
    test_path = "not/a/real/path"

    with pytest.raises(AssertionError) as err:
        test_local_dir_store = LocalDirectoryStore(test_path)

    assert "Given path does not exist as a local directory." in str(err.value)