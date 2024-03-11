from pathlib import Path
import sys

import pytest

# Add repo root path for imports
repo_root = Path(__file__).parent.parent
sys.path.append(str(repo_root.absolute()))


# Fixture for filtering out sensitive/dynamic parameters in UploadClient.upload() HTTP requests
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("X-Florence-Token", "DUMMY")],
        "filter_query_parameters": [
            ("resumableIdentifier", "DUMMY"),
        ],
    }
