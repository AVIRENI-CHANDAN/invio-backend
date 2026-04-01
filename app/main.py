from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
from app.config import (
    APPLICATION_DESCRIPTION,
    APPLICATION_TITLE,
    ApplicationEnvironmentConig,
    VERSION_FILE_NAME,
    APPLICATION_NAME,
    APPLICATION_VERSION,
    APPLICATION_TIMEZONE,
)

from fastapi import FastAPI, HTTPException
from typing import Any, cast

BASE_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = BASE_DIR / VERSION_FILE_NAME
APPLICATION_ENVIRONMENT = cast(
    int,
    f"{os.getenv("APPLICATION_ENVIRONMENT", ApplicationEnvironmentConig.DEVELOPMENT)}".strip(),
)
APPLICATION_RELOAD = APPLICATION_ENVIRONMENT == ApplicationEnvironmentConig.DEVELOPMENT
APP_PORT = int(os.getenv("APP_PORT", "8000"))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")

from app.api import api_router
from app.db.session import init_db


def get_git_commit() -> str:
    """
    Return the current git commit hash if available.

    Returns:
        str: The current git commit hash, or "unknown" if it cannot be determined.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=BASE_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        commit = result.stdout.strip()
        return commit or "unknown"
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def build_version_payload() -> dict[str, str]:
    """
    Build a payload containing deployment metadata, including application name, version, last git commit, and deployment timestamp.

    Returns:
        dict[str, str]: _description_
    """
    deployed_at = datetime.now(APPLICATION_TIMEZONE).replace(microsecond=0).isoformat()
    return {
        "application_name": APPLICATION_NAME,
        "application_version": APPLICATION_VERSION,
        "last_code_commit": get_git_commit(),
        "last_deployment": deployed_at,
    }


def write_version_file() -> dict[str, str]:
    """
    Write deployment metadata to version.json, overwriting any existing file.

    Returns:
        dict[str, str]: The payload that was written to the file.
    """
    if VERSION_FILE.exists():
        VERSION_FILE.unlink()

    payload = build_version_payload()
    VERSION_FILE.write_text(
        json.dumps(payload, indent=4),
        encoding="utf-8",
    )
    return payload


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Deployment metadata is regenerated each app startup."""
    init_db()
    write_version_file()
    yield


app: FastAPI = FastAPI(
    title=APPLICATION_TITLE,
    version=APPLICATION_VERSION,
    description=APPLICATION_DESCRIPTION,
    lifespan=lifespan,
)
app.include_router(api_router)


@app.get("/version", tags=["Deployment"])
def get_version() -> dict[str, str]:
    f"""
    Serve deployment metadata from {VERSION_FILE_NAME}
    
    Returns:
        dict[str, str]: Deployment metadata including application name, version, last git commit, and last deployment timestamp.
    
    Raises:
        HTTPException: If the version file is not found, contains invalid JSON, or is empty
        FileNotFoundError: If the version file does not exist
        json.JSONDecodeError: If the version file contains invalid JSON
        ValueError: If the version file is empty or does not contain a JSON object
    """
    try:
        payload = VERSION_FILE.read_text(encoding="utf-8").strip()
        if not payload:
            raise ValueError(f"{VERSION_FILE_NAME} is empty")

        data: dict[str, Any] | list[Any] = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError(f"{VERSION_FILE_NAME} must contain a JSON object")
        return data
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=f"{VERSION_FILE_NAME} not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"{VERSION_FILE_NAME} contains invalid JSON",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
