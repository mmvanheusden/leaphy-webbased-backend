""" Manage startup / shutdown of the application """
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from conf import settings
from deps.logs import logger
from deps.utils import repeat_every


@asynccontextmanager
async def startup(_app: FastAPI) -> None:
    """Startup context manager"""
    await refresh_library_index()
    yield


@repeat_every(seconds=settings.library_index_refresh_interval, logger=logger)
async def refresh_library_index():
    """Update the Arduino library index"""
    logger.info("Updating library index...")
    installer = await asyncio.create_subprocess_exec(
        settings.arduino_cli_path,
        "lib",
        "update-index",
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await installer.communicate()
    if installer.returncode != 0:
        raise EnvironmentError(
            f"Failed to update library index: {stderr.decode() + stdout.decode()}"
        )