import logging
import pathlib
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

import uvicorn
from fastapi import FastAPI

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
    app.include_router(gateway_router)

    return app


def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    app = create_app(settings)
    uvicorn.run(
        app=app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    )


if __name__ == "__main__":
    main()
