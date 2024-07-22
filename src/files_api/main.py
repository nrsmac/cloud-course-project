"""Main module for the files API."""

import pydantic
from fastapi import FastAPI
from fastapi.routing import APIRoute

from files_api.errors import (
    handle_broad_exceptions,
    handle_pydantic_validation_errors,
)
from files_api.routes import ROUTER
from files_api.settings import Settings


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a FastAPI application with the specified S3 bucket name."""
    settings = settings or Settings()

    app = FastAPI(
        title="Files API",
        description="An API to upload and retrieve files.",
        generate_unique_id_function=custom_generate_unique_id,
        version="0.1.0",
    )
    app.state.settings = settings

    app.include_router(ROUTER)
    app.add_exception_handler(
        exc_class_or_status_code=pydantic.ValidationError,
        handler=handle_pydantic_validation_errors,
    )
    app.middleware("http")(handle_broad_exceptions)

    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore

    app: FastAPI = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
