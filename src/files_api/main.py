import os

from fastapi import FastAPI

from files_api.routes import ROUTER


def create_app(s3_bucket_name: str | None = None) -> FastAPI:
    """Create a FastAPI application with the specified S3 bucket name."""
    s3_bucket_name = s3_bucket_name or os.getenv("s3_bucket_name")  # noqa: F821

    app = FastAPI()
    app.state.s3_bucket_name = s3_bucket_name

    app.include_router(ROUTER)

    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore

    app: FastAPI = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
