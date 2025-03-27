import logging
import os
import pathlib
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.limiter import init_limiter

root_path = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.config import Settings, get_settings
from src.api import gateway_router


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=settings.LOGGING_LEVEL,
        format=settings.LOGGING_FORMAT,
    )


def create_app(settings: Settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        redis = aioredis.from_url(url=settings.redis_url)  # type: ignore[no-untyped-call]
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        yield

    app = FastAPI(
        title="Notifications service API",
        description="This service provides notifications API",
        version="0.1.0",
        redoc_url=None,
        docs_url="/api/docs",
        debug=True,
        lifespan=lifespan,
    )
    mount_views(app)
    app.include_router(gateway_router)

    return app


def mount_views(app: FastAPI) -> None:
    script_dir = os.path.dirname(__file__)
    static_dir = os.path.join(script_dir, "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def add_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    app = create_app(settings)
    init_limiter(app)
    Instrumentator().instrument(app).expose(app)
    add_cors_middleware(app)
    uvicorn.run(
        app=app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    )


if __name__ == "__main__":
    main()
