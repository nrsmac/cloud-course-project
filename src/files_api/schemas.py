from datetime import datetime
from typing import (
    List,
    Optional,
)

from pydantic import BaseModel


class FileMetadata(BaseModel):
    """Represents metadata of a file."""

    file_path: str
    last_modified: datetime
    size_bytes: int


# more pydantic models ...
class PutFileResponse(BaseModel):
    """Response schema for uploading a file."""

    file_path: str
    message: str


class GetFilesQueryParams(BaseModel):
    """Query parameters for listing files."""

    page_size: Optional[int] = 10
    directory: Optional[str] = ""
    page_token: Optional[str] = None


class ListFilesResponse(BaseModel):
    """Response schema for listing files."""

    files: List[FileMetadata]
    next_page_token: Optional[str]
