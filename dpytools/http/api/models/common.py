from enum import Enum


class DatasetState(Enum):
    CREATED = "created"
    COMPLETED = "completed"
    FAILED = "failed"
    EDITION_CONFIRMED = "edition-confirmed"
    ASSOCIATED = "associated"
    PUBLISHED = "published"
