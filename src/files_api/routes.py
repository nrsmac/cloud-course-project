"""API routes for the files API."""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object
from files_api.schemas import (
    FileMetadata,
    GetFilesQueryParams,
    GetFilesResponse,
    PutFileResponse,
)
from files_api.settings import Settings

ROUTER = APIRouter()


@ROUTER.put("/v1/files/{file_path:path}")
async def upload_file(
    request: Request, file_path: str, file_content: UploadFile, response: Response
) -> PutFileResponse:
    """Upload a file."""
    settings: Settings = request.app.state.settings
    object_already_exists = object_exists_in_s3(
        bucket_name=settings.s3_bucket_name, object_key=file_path
    )  # noqa: F821

    if object_already_exists:
        response_message = f"File already exists at path: /{file_path}"
        response.status_code = status.HTTP_200_OK
    else:
        response_message = f"File uploaded successfully at path: /{file_path}"
        response.status_code = status.HTTP_201_CREATED

    file_contents: bytes = await file_content.read()

    upload_s3_object(
        bucket_name=settings.s3_bucket_name,
        object_key=file_path,
        file_content=file_contents,
        content_type=file_content.content_type,
    )
    return PutFileResponse(file_path=file_path, message=response_message)


@ROUTER.get("/v1/files")
async def list_files(
    request: Request,
    query_params: GetFilesQueryParams = Depends(),
) -> GetFilesResponse:
    """List files with pagination."""
    settings: Settings = request.app.state.settings
    if query_params.page_token:
        files, next_page_token = fetch_s3_objects_using_page_token(
            bucket_name=settings.s3_bucket_name,
            continuation_token=query_params.page_token,
            max_keys=query_params.page_size,
        )
    else:
        files, next_page_token = fetch_s3_objects_metadata(
            bucket_name=settings.s3_bucket_name,
            prefix=query_params.directory,
            max_keys=query_params.page_size,
        )

    file_metadata_objs = [
        FileMetadata(
            file_path=f"{item['Key']}",
            last_modified=item["LastModified"],
            size_bytes=item["Size"],
        )
        for item in files
    ]
    return GetFilesResponse(files=file_metadata_objs, next_page_token=next_page_token if next_page_token else None)


@ROUTER.head("/v1/files/{file_path:path}")
async def get_file_metadata(request: Request, file_path: str, response: Response) -> Response:
    """
    Retrieve file metadata.

    Note: by convention, HEAD requests MUST NOT return a body in the response.
    """
    settings: Settings = request.app.state.settings

    object_exists = object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    get_object_response = fetch_s3_object(settings.s3_bucket_name, object_key=file_path)
    response.headers["Content-Type"] = get_object_response["ContentType"]
    response.headers["Content-Length"] = str(get_object_response["ContentLength"])
    response.headers["Last-Modified"] = get_object_response["LastModified"].strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.status_code = status.HTTP_200_OK
    return response


@ROUTER.get("/v1/files/{file_path:path}")
async def get_file(
    request: Request,
    file_path: str,
) -> StreamingResponse:
    """Retrieve a file."""
    settings: Settings = request.app.state.settings

    object_exists = object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    get_object_response = fetch_s3_object(bucket_name=settings.s3_bucket_name, object_key=file_path)
    return StreamingResponse(
        content=get_object_response["Body"],
        media_type=get_object_response["ContentType"],
    )


@ROUTER.delete("/v1/files/{file_path:path}")
async def delete_file(
    request: Request,
    file_path: str,
    response: Response,
) -> Response:
    """
    Delete a file.

    NOTE: DELETE requests MUST NOT return a body in the response.
    """
    settings: Settings = request.app.state.settings

    object_exists = object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    delete_s3_object(bucket_name=settings.s3_bucket_name, object_key=file_path)
    response.status_code = status.HTTP_200_OK
    return response
