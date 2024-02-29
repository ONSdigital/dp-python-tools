import os
from tempfile import TemporaryDirectory
import pytest
from pathlib import Path, PosixPath

from dpytools.stores.directory.local import LocalDirectoryStore

# note, directory doesnt matter, we're just using this
# as it'll always exist here relatively.
TEST_DIRECTORY = Path(__file__).parent.parent.parent.absolute()


def test_local_directory_store_path():
    """
    Ensures a LocalDirectoryStore can be instantiated from a
    given Path and that it can store the path to a correct
    existing local directory.
    """

    test_path = Path(TEST_DIRECTORY)

    test_local_dir_store = LocalDirectoryStore(test_path)

    assert test_local_dir_store.local_path == PosixPath(TEST_DIRECTORY)


def test_local_directory_store_string():
    """
    Ensures a LocalDirectoryStore can be instantiated from a
    given string, and that string can be converted to a Path
    which represents a correct existing local directory.
    """

    test_path = TEST_DIRECTORY

    test_local_dir_store = LocalDirectoryStore(test_path)

    assert test_local_dir_store.local_path == PosixPath(TEST_DIRECTORY)


def test_local_directory_store_non_existing():
    """
    Ensures a LocalDirectoryStore object instantiated with a
    given input that is a Path object or can be converted to a
    Path raises the expected error if the path does not exist locally.
    """

    test_path = "not/a/real/path"

    with pytest.raises(AssertionError) as err:
        LocalDirectoryStore(test_path)

    assert "Given path not/a/real/path does not exist." in str(err.value)


def test_local_directory_store_non_directory():
    """
    Ensures a LocalDirectoryStore object instantiated with a
    given input that is a Path object or can be converted to a
    Path raises the expected error if the path is not a directory.
    """

    test_path = Path(f"{TEST_DIRECTORY}/conftest.py").absolute()

    with pytest.raises(AssertionError) as err:
        LocalDirectoryStore(test_path)

    assert "is not a directory." in str(err.value)


def test_add_file_as_string():
    """
    Ensures that the specified file is added to the local directory store.
    """
    with TemporaryDirectory() as tmp_dir:
        test_local_dir_store = LocalDirectoryStore(tmp_dir)
        file = "tests/test_cases/test_local_store/data.csv"
        file_path = test_local_dir_store.add_file(file)
        with open(file_path, "rb") as fp:
            store_file = fp.read()
        assert file_path.name in os.listdir(tmp_dir)
        assert len(store_file) == 207


def test_add_file_as_path():
    """
    Ensures that the specified file is added to the local directory store.
    """
    with TemporaryDirectory() as tmp_dir:
        test_local_dir_store = LocalDirectoryStore(tmp_dir)
        file = Path("tests/test_cases/test_local_store/data.csv")
        file_path = test_local_dir_store.add_file(file)
        with open(file_path, "rb") as fp:
            store_file = fp.read()
        assert file_path.name in os.listdir(tmp_dir)
        assert len(store_file) == 207


def test_add_file_does_not_exist():
    """
    Ensures that an error is raised if the file to be added to the local directory store does not exist.
    """
    with TemporaryDirectory() as tmp_dir:
        test_local_dir_store = LocalDirectoryStore(tmp_dir)
        file = Path("tests/test_cases/test_local_store/does_not_exist.csv")
        with pytest.raises(AssertionError) as err:
            test_local_dir_store.add_file(file)
        assert (
            "Given file tests/test_cases/test_local_store/does_not_exist.csv does not exist."
            in str(err.value)
        )


def test_get_file_names():
    """
    Ensures that the `get_file_names()` method returns the correct number of files
    """
    test_local_dir_store = LocalDirectoryStore("tests/test_cases/test_local_store")
    file_names = test_local_dir_store.get_file_names()
    assert len(file_names) == 3
    assert "data.csv" in file_names


def test_get_file_names_no_files():
    with TemporaryDirectory() as tmp_dir:
        test_local_dir_store = LocalDirectoryStore(tmp_dir)
        with pytest.raises(ValueError) as err:
            test_local_dir_store.get_file_names()
        assert "No files found in given directory" in str(err.value)


def test_get_current_source_pathlike():
    """
    Ensures that the `get_current_source_pathlike()` method returns the LocalDirectoryStore.local_path as a string
    """
    with TemporaryDirectory() as tmp_dir:
        test_local_dir_store = LocalDirectoryStore(tmp_dir)
        current_source_pathlike = test_local_dir_store.get_current_source_pathlike()
        tmp_dir_absolute = Path(tmp_dir).absolute()
        assert current_source_pathlike == str(tmp_dir_absolute)
