"""Pydantic schemas for the files API."""

import re
from datetime import datetime
from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)
from typing_extensions import Self

DEFAULT_GET_FILES_PAGE_SIZE = 10
DEFAULT_GET_FILES_MIN_PAGE_SIZE = 10
DEFAULT_GET_FILES_MAX_PAGE_SIZE = 100
DEFAULT_GET_FILES_DIRECTORY = ""


def is_valid_path(value: str) -> bool:
    """Validate minimum and maximum length and regex of a path."""
    valid_path_patern = r"^([/a-zA-Z0-9_.-])+(/[a-zA-Z0-9_.-]+)*$"
    if len(value) < 1 or len(value) > 1024 or not re.match(valid_path_patern, value):
        return False
    return True


class FileMetadata(BaseModel):
    """Schema for file metadata."""

    file_path: str
    last_modified: datetime
    size_bytes: int

    @model_validator(mode="after")
    def check_for_valid_path(self) -> Self:
        """Validate minimum and maximum length and regex of a path."""
        if not is_valid_path(self.file_path):
            raise ValueError("Invalid file path")
        return self


class GetFilesResponse(BaseModel):
    """Response schema for listing files."""

    files: List[FileMetadata]
    next_page_token: Optional[str]


class GetFilesQueryParams(BaseModel):
    """Query parameters schema for listing files."""

    page_size: int = Field(
        default=DEFAULT_GET_FILES_PAGE_SIZE,
        ge=DEFAULT_GET_FILES_MIN_PAGE_SIZE,
        le=DEFAULT_GET_FILES_MAX_PAGE_SIZE,
    )
    directory: str = DEFAULT_GET_FILES_DIRECTORY
    page_token: Optional[str] = None

    @model_validator(mode="after")
    def check_page_token_is_mutually_exclusive_with_page_size_and_directory(self) -> Self:
        """Validate page_token is mutually exclusive with page_size and directory."""
        if self.page_token:
            get_files_query_params: dict = self.model_dump(exclude_unset=True)
            page_size_set = "page_size" in get_files_query_params.keys()
            directory_set = "directory" in get_files_query_params.keys()
            if page_size_set or directory_set:
                raise ValueError("page_token is mutually exclusive with page_size and directory")
        return self


class DeleteFileResponse(BaseModel):
    """Response schema for deleting a file."""

    message: str


class PutFileResponse(BaseModel):
    """Response schema for uploading a file."""

    file_path: str
    message: str

    @model_validator(mode="after")
    def check_for_valid_path(self) -> Self:
        """Validate minimum and maximum length and regex of a path."""
        if not is_valid_path(self.file_path):
            raise ValueError("Invalid file path")
        return self
