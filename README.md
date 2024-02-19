WORK IN PROGRESS - DO NOT USE

# dp-python-tools

_Simple_ reusable python classes and functions for digital publishing.

The key word is _simple_. If the desired functionality is more than a script or two (or existing functionality sprawls beyond that) please consider separating it into it's own repository.

Given this pattern, each distinct thing should be clearly separated out within `./pytools` with each having its own README with example usage.

TLDR: Try and enforce decent logical separation between the tools in this toolbag against the eventuality/likelyhood of separating them out at a later date.

## Installation
This repository is provided as an installable python package

1. **Install the package**

    Open your terminal and run the following command:

    ```bash
    pip install git+https://github.com/ONSdigital/dp-python-tools.git
    ```

## Development

All commits that make it to PR should have black and ruff already ran against them, you can do this via `make fmt` and you can lint via `make lint`.

Given this is a lower level resource to be relied on by other things, all classes and functions should have good unit test coverage. You can run the unit tests via `make test`.

Licence
-------

Copyright ©‎ 2024, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.