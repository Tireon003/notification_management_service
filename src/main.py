import logging
import pathlib
import sys

import uvicorn
from fastapi import FastAPI

root_path = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.config import Settings
from src.api import gateway_router


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=settings.LOGGING_LEVEL,
        format=settings.LOGGING_FORMAT,
    )


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Notifications service API",
        description="This service provides notifications API",
        version="0.1.0",
        redoc_url=None,
        docs_url="/api/docs",
        debug=True,
    )
    app.include_router(gateway_router)

    return app


def main() -> None:
    settings = Settings()
    configure_logging(settings)
    app = create_app(settings)
    uvicorn.run(
        app=app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    )


if __name__ == "__main__":
    main()
