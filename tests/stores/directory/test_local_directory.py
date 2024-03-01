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


def test_get_current_source_pathlike():
    """
    Ensures that the `get_current_source_pathlike()` method returns the LocalDirectoryStore.local_path as a string
    """
    with TemporaryDirectory() as tmp_dir:
        test_local_dir_store = LocalDirectoryStore(tmp_dir)
        current_source_pathlike = test_local_dir_store.get_current_source_pathlike()
        tmp_dir_absolute = Path(tmp_dir).absolute()
        assert current_source_pathlike == str(tmp_dir_absolute)


def test_has_lone_file_matching():
    """
    Checks that a LocalDirectoryStore can run the has_lone_file_matching()
    function against its local directory and successfully returns True if 
    the directory has only one file matching the given pattern.
    """

    test_path = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_lone_file")
    test_local_directory_store = LocalDirectoryStore(test_path)

    assert test_local_directory_store.has_lone_file_matching(".json")

def test_has_lone_file_matching_none():
    """
    Checks that a LocalDirectoryStore can run the has_lone_file_matching()
    function against its local directory and successfully returns False if 
    the directory has zero files that match the given pattern.
    """

    test_path = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_lone_file")
    test_local_directory_store = LocalDirectoryStore(test_path)

    assert not test_local_directory_store.has_lone_file_matching(".py")


def test_has_lone_file_matching_multiple():
    """
    Checks that a LocalDirectoryStore can run the has_lone_file_matching()
    function against its local directory and successfully returns False if 
    the directory has more than one file that matches the given pattern.
    """

    test_path = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_multiple_file")
    test_local_directory_store = LocalDirectoryStore(test_path)

    with pytest.raises(FileNotFoundError) as err:
        test_local_directory_store.has_lone_file_matching(".json")
    assert "More than 1 file found that matches the regex pattern '.json' in directory tests/test_cases/test_local_store/local_directory_folders/local_directory_multiple_file. Matching: ['local_directory2.json', 'local_directory1.json']" == str(err.value)


def test_save_lone_file_destination():
    """
    Checks that a LocalDirectoryStore can retrieve a lone matching file 
    from a given pattern in its local path directory, and save that file 
    in another destination directory.
    """

    test_path = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_lone_file")
    test_local_directory_store = LocalDirectoryStore(test_path)

    destination_dir = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_destination")

    test_local_directory_store.save_lone_file_matching(".json", destination_dir)
    test_result_file = destination_dir / "local_directory_test.json"

    assert test_result_file.exists()

    # Delete the saved file after test is completed.
    os.remove(test_result_file)


def test_save_lone_file_destination_file_already_exists():
    """
    Checks that a LocalDirectoryStore can retrieve a lone matching file 
    from a given pattern in its local path directory, but the expected 
    error is returned if the file already exists in the destination 
    directory when trying to save it.
    """

    test_path = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_lone_file")
    test_local_directory_store = LocalDirectoryStore(test_path)

    destination_dir = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_destination_error")

    with pytest.raises(ValueError) as err:
        test_local_directory_store.save_lone_file_matching(".json", destination_dir)

    assert (
    "Given file already exists in directory tests/test_cases/test_local_store/local_directory_folders/local_directory_destination_error/local_directory_test.json"
     == str(err.value)
    )


def test_get_file_names():
    """
    Checks that a list of file names can be retrieved 
    from a LocalDirectoryStore's local path directory as a list.
    """

    test_path = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_multiple_file")
    test_local_directory_store = LocalDirectoryStore(test_path)

    file_name_list = test_local_directory_store.get_file_names()

    assert len(file_name_list) == 2
    assert file_name_list[0] == "local_directory2.json"
    assert file_name_list[1] == "local_directory1.json"


def test_get_file_names_no_files():
    """
    Checks that an empty list is returned as expected when 
    no matching files are found in the given directory.
    """
    test_path_dir = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_no_files")
    test_path_dir.mkdir(exist_ok=True)
    test_local_directory_store = LocalDirectoryStore(test_path_dir)

    file_name_list = test_local_directory_store.get_file_names()

    assert file_name_list == []
    
    Path.rmdir(test_path_dir)


def test_get_lone_file_matching_json_dict():
    """
    Ensures a LocalDirectoryStore's local path directory containing one json file 
    can successfully acquire a match for that json file given a regex pattern 
    and return a dictionary of that json file's contents.
    """

    test_path = Path("tests/test_cases/test_local_store/local_directory_folders/local_directory_lone_file")
    test_local_directory_store = LocalDirectoryStore(test_path)

    local_file_json_dict = test_local_directory_store.get_lone_matching_json_as_dict(".json")

    assert local_file_json_dict["schema"] == "airflow.schemas.ingress.sdmx.v1.schema.json"
    assert local_file_json_dict["priority"] == 1
    assert local_file_json_dict["pipeline"] == "default"
