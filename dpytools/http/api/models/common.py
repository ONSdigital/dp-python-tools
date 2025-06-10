from enum import Enum

from pydantic import Field


class DatasetState(str, Enum):
    NOT_SET = "not_set"
    CREATED = "created"
    COMPLETED = "completed"
    FAILED = "failed"
    EDITION_CONFIRMED = "edition-confirmed"
    ASSOCIATED = "associated"
    PUBLISHED = "published"


DefaultedDatasetStateField = Field(default=DatasetState.NOT_SET)
