from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from dpytools.http.api.models.common import DatasetState, DefaultedDatasetStateField


class Distribution(BaseModel):
    title: Optional[str] = None
    format: Optional[str] = None
    file: Optional[str] = None
    download_url: Optional[str] = Field(default=None, init=False)
    media_type: Optional[str] = Field(default=None, init=False)


class Alert(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None


class UsageNote(BaseModel):
    title: Optional[str] = None
    note: Optional[str] = None


class SubmissionContact(BaseModel):
    email: EmailStr


class DatasetVersion(BaseModel):
    edition_title: Optional[str] = None
    edition: Optional[str] = None
    distributions: List[Distribution] = Field(default_factory=list)
    release_date: Optional[datetime | str] = None
    quality_designation: Optional[str] = None
    usage_notes: Optional[List[UsageNote]] = Field(default_factory=list)
    alerts: Optional[List[Alert]] = Field(default_factory=list)
    state: DatasetState = DefaultedDatasetStateField
    version: int = 0


class GetDatasetVersionsResponse(BaseModel):
    items: List[DatasetVersion] = Field(default_factory=list)

    def get_latest_version(self) -> Optional[DatasetVersion]:
        return (
            None
            if len(self.items) == 0
            else max(self.items, key=lambda version: version.version)
        )

    def can_publish_new_version(
        self, expected_state: DatasetState = DatasetState.PUBLISHED
    ) -> bool:
        latest_version = self.get_latest_version()

        return (
            True if latest_version is None else latest_version.state == expected_state
        )
