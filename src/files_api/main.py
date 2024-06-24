import os
from datetime import datetime
from typing import (
    List,
    Optional,
)

import pendulum
from fastapi import (
    Depends,
    FastAPI,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object

####################################
# --- Request/response schemas --- #
####################################


# read (cRud)
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


def create_app(s3_bucket_name: str | None = None) -> FastAPI:
    s3_bucket_name = s3_bucket_name or os.getenv("s3_bucket_name")  # noqa: F821
    app = FastAPI()

    @app.put("/files/{file_path:path}")
    async def upload_file(file_path: str, file: UploadFile, response: Response) -> PutFileResponse:
        """Upload a file."""
        object_already_exists = object_exists_in_s3(bucket_name=s3_bucket_name, object_key=file_path)

        if object_already_exists:
            response_message = f"File already exists at path: /{file_path}"
            response.status_code = status.HTTP_200_OK
        else:
            response_message = f"File uploaded successfully at path: /{file_path}"
            response.status_code = status.HTTP_201_CREATED

        file_contents: bytes = await file.read()

        upload_s3_object(
            bucket_name=s3_bucket_name,
            object_key=file_path,
            file_content=file_contents,
            content_type=file.content_type,
        )
        return PutFileResponse(file_path=file_path, message=response_message)

    @app.get("/files")
    async def list_files(
        query_params: GetFilesQueryParams = Depends(),
    ) -> ListFilesResponse:
        """List files with pagination."""
        if query_params.page_token:
            files, next_page_token = fetch_s3_objects_using_page_token(
                bucket_name=s3_bucket_name,
                continuation_token=query_params.page_token,
                max_keys=query_params.page_size,
            )
        else:
            files, next_page_token = fetch_s3_objects_metadata(
                bucket_name=s3_bucket_name,
                prefix=query_params.directory if query_params.directory else "",
                max_keys=query_params.page_size,
            )

        file_metadata_objects = [
            FileMetadata(
                file_path=f"{file['Key']}",
                last_modified=file["LastModified"],
                size_bytes=file["Size"],
            )
            for file in files
        ]

        return ListFilesResponse(
            files=file_metadata_objects, next_page_token=next_page_token if next_page_token else None
        )

    @app.head("/files/{file_path:path}")
    async def get_file_metadata(file_path: str, response: Response) -> Response:
        """
        Retrieve file metadata.

        Note: by convention, HEAD requests MUST NOT return a body in the response.
        """
        s3_object = fetch_s3_object(bucket_name=s3_bucket_name, object_key=file_path)

        response.headers["Content-Length"] = str(s3_object["ContentLength"])
        response.headers["Last-Modified"] = pendulum.instance(s3_object["LastModified"]).to_rfc1123_string()
        response.headers["Content-Type"] = s3_object["ContentType"]
        response.status_code = status.HTTP_200_OK

        return response

    @app.get("/files/{file_path:path}")
    async def get_file(
        file_path: str,
    ) -> StreamingResponse:
        """Retrieve a file."""
        s3_object = fetch_s3_object(bucket_name=s3_bucket_name, object_key=file_path)
        return StreamingResponse(
            content=s3_object["Body"],
            media_type=s3_object["ContentType"],
        )

    @app.delete("/files/{file_path:path}")
    async def delete_file(
        file_path: str,
        response: Response,
    ) -> Response:
        """
        Delete a file.

        NOTE: DELETE requests MUST NOT return a body in the response.
        """
        delete_s3_object(bucket_name=s3_bucket_name, object_key=file_path)
        response.status_code = status.HTTP_200_OK
        return response

    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore

    app: FastAPI = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
