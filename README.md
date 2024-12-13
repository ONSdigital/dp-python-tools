# dp-python-tools

_Simple_ reusable python classes and functions for digital publishing.

The key word is _simple_. If the desired functionality is more than a script or two (or existing functionality sprawls beyond that) please consider separating it into its own repository.

Given this pattern, each distinct tool should be clearly separated out within `./dpytools`, with each tool having its own README with example usage.

TLDR: Try and enforce decent logical separation between the tools in this toolbag against the eventuality/likelyhood of separating them out at a later date.

## Installation

This repository is provided as an installable python package.

1. **To install the package**

    Open your terminal and run the following command:

    ```bash
    pip install git+https://github.com/ONSdigital/dp-python-tools.git
    ```

## Development

All commits that make it to PR should have had `black` and `ruff` already run against them, you can do this via `make fmt` and you can lint via `make lint`.

Given this is a lower level resource to be relied on by other things, all classes and functions should have good unit test coverage. You can run the unit tests via `make test`.

## To Run Locally
Make sure you have the correct version of python installed. Check poetry.lock for the versions allowed (python-versions = ">=3.9, <3.12"). Create a virtual env  with correct python version with the command. (Note make sure your venv is called .venv as in the .gitignore)
```
python3.11 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

## Release process

This package follows standard [semantic versioning](https://semver.org/) for its release process. Releases are tagged as vX.Y.Z, where:

- X denotes the MAJOR version (significant new functionality released which is not backwards-compatible with earlier versions).
- Y denotes the MINOR version (new functionality released which is backwards-compatible with earlier versions).
- Z denotes the PATCH version (no new functionality, backwards-compatible, primarily used for bug fixes).

To release a new version of `dpytools`:

1. In the `[tool.poetry]` section of `pyproject.toml`, update the `version` number as appropriate, following the semantic versioning rules listed above.
2. Commit the `pyproject.toml` changes to git, and merge to the `develop` branch.
3. In the GitHub repository, click "Releases" in the right-hand column.
4. Click the "Draft a new release" button in the top right corner of the Releases page.
5. Click the "Choose a tag" dropdown, and enter the new version number, **ensuring that this matches the updated version number in `pyproject.toml`**. Click "Create new tag".
6. Ensure that "Target" is set to "develop".
7. Click the "Previous tag" dropdown and select the most recent release tag from the list.
8. Click "Generate release notes" to automatically generate a description for the release. This is essentially a list of all branches merged since the previous release. You can manually edit these notes to make it easier to read for end users, if desired.
9. By default, the "Release title" defaults to the version tag - add a short description of changes that have been made in the new version.
10. Click "Publish release" to release the new version of the package.

Licence
-------

Copyright ©‎ 2024, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.