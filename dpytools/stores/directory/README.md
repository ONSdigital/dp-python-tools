# dpytools: LocalDirectoryStore

A class implementing the BaseWritableSingleDirectoryStore base class. LocalDirectoryStore provides access to several functions related to retrieving, saving, 
getting information and performing regex pattern matching on files in a given directory that has a path

## Usage

This section will describe the basic properties of the class, then go into detail on the available functionality that can be used on a LocalDirectoryStore object.

### Creating a LocalDirectoryStore object

To create an instance of the LocalDirectoryStore, only one parameter is required to be input: `local_dir`. This can either be a Path object, or a string, which represents the path of the directory used as the local store.

The class' `__init__` functionality converts the `local_dir` to a Path type if it is a string, then performs basic checks to ensure the specified path exists, and that it is a directory (rather than a file). When a LocalDirectoryStore object is instansiated, this `local_dir` input becomes assigned as the `local_dir` variable, which is the only property of this class.

This is how a LocalDirectoryStore object can be created with a Path variable as input:

```python
from dpytools.stores.directory.local import LocalDirectoryStore

my_path = Path("my/path/directory/")

my_store = LocalDirectoryStore(my_path)
```

This is how a LocalDirectoryStore object can be created with a string variable as input:

```python
from dpytools.stores.directory.local import LocalDirectoryStore

my_store = LocalDirectoryStore("my/path/directory/")
```

## Functions with examples

### add_file

Adds a specified file to the directory of the LocalDirectoryStore. The file's current directory must be given as a string or Path type input parameter.

Some basic validation is performed to ensure the given file is a Path type object (it is converted to a Path if it is a string), and to ensure it is a file that exists. The file is then saved to the directory of the local store.

Example of this function being used:

```python
    store_path = Path("my/store/path/")
    my_store = LocalDirectoryStore(store_path)

    file_to_add = Path("my/file/path")

    my_store.add_file(file_to_add)
```

### get_file_names

A function that is mainly used to aid development of other functions. It gets a list of the files in the local store directory.

If the directory is empty, then an empty list is returned.

### has_lone_file_matching

Gets the list of files that exist in the local store directory, then checks that only one file matching the given input pattern exists in that list, 
returning a boolean of the result.

An example of this function being used on a LocalDirectoryStore, in this case checking that only one file has the pattern ".json":

```python
    test_path = Path(
        "my_directory/local_directory_lone_json_file"
    )
    test_local_directory_store = LocalDirectoryStore(test_path)

    test_local_directory_store.has_lone_file_matching(".json")

```

If there are no matching files, then False is returned. If multiple files matching the specified pattern are found, a FileNotFound error is raised.

### save_lone_file_matching

Asserts that only one file matching the given pattern exists (using has_lone_file_matching), then saves that file to a directory. The save destination directory is optionally given as an input parameter that can be a string or a Path (if it is a string, it is converted to a Path). If no save destination directory is given, then the matching file is saved in the current directory.

Here is an example of this function being used to save a file matching the pattern ".txt" to a specific destination.

```python
directory_store_path = "my/store/path/"

directory_store = LocalDirectoryStore(directory_store_path)

save_directory = "save/destination/"

directory_store.save_lone_file_matching("txt", save_directory)

```

If the file to be saved already exists in the save destination, or the save destination does not exist, an error is returned.

### get_lone_matching_json_as_dict

Asserts the directory has one file matching the specified pattern, then loads that file's contents to a json object and returns the json as a python dictionary.
Using this function in code would be no different to `has_lone_file_matching` as only an input pattern is required.

### _files_that_match_pattern

A private utility function that is used to aid development of other functions. This function is used on `self` to retrieve a list of files in the local store directory, but also performs a matching operation to only include files that match a specified pattern. By indexing the returned list, the files in the directory can be accessed without needing to know their exact path or names. This is showcased in the example below:

```python
file_to_get = self._files_that_match_pattern(pattern)[0]
```

### get_current_source_pathlike

Returns the local path of the directory store, in absolute form.

Example usage on a local directory store with the path "/my_directory/store/":

```python
test_local_dir_store = LocalDirectoryStore("/my_directory/store/")

current_source_pathlike = test_local_dir_store.get_current_source_pathlike()

# current_source_pathlike would be "/my_directory/store"

```