import pendulum
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    UploadFile,
    status,
    HTTPException,
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
    ListFilesResponse,
    PutFileResponse,
)
from files_api.settings import Settings

ROUTER = APIRouter()


@ROUTER.put("/files/{file_path:path}")
async def upload_file(request: Request, file_path: str, file: UploadFile, response: Response) -> PutFileResponse:
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

    file_contents: bytes = await file.read()

    upload_s3_object(
        bucket_name=settings.s3_bucket_name,
        object_key=file_path,
        file_content=file_contents,
        content_type=file.content_type,
    )
    return PutFileResponse(file_path=file_path, message=response_message)


@ROUTER.get("/files")
async def list_files(
    request: Request,
    query_params: GetFilesQueryParams = Depends(),
) -> ListFilesResponse:
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

    return ListFilesResponse(files=file_metadata_objects, next_page_token=next_page_token if next_page_token else None)


@ROUTER.head("/files/{file_path:path}")
async def get_file_metadata(request: Request, file_path: str, response: Response) -> Response:
    """
    Retrieve file metadata.

    Note: by convention, HEAD requests MUST NOT return a body in the response.
    """
    settings: Settings = request.app.state.settings

    object_exists = object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    s3_object = fetch_s3_object(bucket_name=settings.s3_bucket_name, object_key=file_path)

    response.headers["Content-Length"] = str(s3_object["ContentLength"])
    response.headers["Last-Modified"] = pendulum.instance(s3_object["LastModified"]).to_rfc1123_string()
    response.headers["Content-Type"] = s3_object["ContentType"]
    response.status_code = status.HTTP_200_OK

    return response


@ROUTER.get("/files/{file_path:path}")
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


@ROUTER.delete("/files/{file_path:path}")
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

    # TODO how can I refactor this?
    object_exists = object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    delete_s3_object(bucket_name=settings.s3_bucket_name, object_key=file_path)
    response.status_code = status.HTTP_200_OK
    return response
