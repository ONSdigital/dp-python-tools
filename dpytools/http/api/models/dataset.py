from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from dpytools.http.api.models.common import DatasetState


class Contact(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    telephone: Optional[str] = None


class Editions(BaseModel):
    href: Optional[str] = None


class IsBasedOn(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None


class LatestEdition(BaseModel):
    href: Optional[str] = None


class LatestVersion(BaseModel):
    href: Optional[str] = None
    id: Optional[str] = None


class DatasetSelf(BaseModel):
    href: Optional[str] = None


class Taxonomy(BaseModel):
    href: Optional[str] = None


class Links(BaseModel):
    editions: Optional[Editions] = None
    latest_version: Optional[LatestVersion] = None
    latest_edition: Optional[LatestEdition] = None
    self: Optional[DatasetSelf] = None
    taxonomy: Optional[Taxonomy] = None


class Methodology(BaseModel):
    href: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class Publication(BaseModel):
    href: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class Publisher(BaseModel):
    name: Optional[str] = None
    href: Optional[str] = None


class Qmi(BaseModel):
    href: Optional[str] = None


class RelatedContent(BaseModel):
    href: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class RelatedDataset(BaseModel):
    href: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class DatasetType(str, Enum):
    FILTERABLE = "filterable"
    CANTABULAR_FLEXIBLE_TABLE = "cantabular_flexible_table"
    CANTABULAR_MULTIVARIATE_TABLE = "cantabular_multivariate_table"
    STATIC = "static"


class Dataset(BaseModel):
    canonical_topic: Optional[str] = None
    collection_id: Optional[str] = None
    contacts: List[Contact] = Field(default_factory=list)
    description: Optional[str] = None
    is_based_on: Optional[IsBasedOn] = None
    keywords: List[str] = Field(default_factory=list)
    last_updated: Optional[str] = None
    license: Optional[str] = None
    links: Optional[Links] = None
    methodologies: List[Methodology] = Field(default_factory=list)
    national_statistic: Optional[bool] = None
    next_release: Optional[str] = None
    publications: List[Publication] = Field(default_factory=list)
    publishers: List[Publisher] = Field(default_factory=list)
    qmi: Optional[Qmi] = None
    related_datasets: List[RelatedDataset] = Field(default_factory=list)
    related_content: List[RelatedContent] = Field(default_factory=list)
    release_frequency: Optional[str] = None
    state: DatasetState
    subtopics: List[str] = Field(default_factory=list)
    survey: Optional[str] = None
    title: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    type: DatasetType
    unit_of_measure: Optional[str] = None


class GetDatasetResponse(BaseModel):
    id: Optional[str] = None
    current: Optional[Dataset] = None
    next: Optional[Dataset] = None

    def can_publish_new_version(
        self,
        expected_state: DatasetState = DatasetState.PUBLISHED,
        expected_type: DatasetType = DatasetType.STATIC,
    ) -> bool:
        versions = [
            Dataset(**version) if isinstance(version, dict) else version
            for version in [self.current, self.next]
        ]
        valid = [
            version.state == expected_state and version.type == expected_type
            for version in versions
            if version is not None
        ]
        return all(valid)
