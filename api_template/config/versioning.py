from fastapi import APIRouter, FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from api_template.api.v1.controllers import user_controller as v1_user


class APIVersion:
    V1 = "v1"
    V2 = "v2"


def register_versioned_routers(app: FastAPI):
    """Register versioned API routers to the FastAPI app."""
    # Register version 1 routers
    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(v1_user.router)
    app.include_router(v1_router)

    # Register version 2 routers
    # v2_router = APIRouter(prefix="/api/v2")
    # v2_router.include_router(v2_user.router)
    # app.include_router(v2_router)


class VersionDeprecationMiddleware(BaseHTTPMiddleware):
    """Middleware to add deprecation warnings to older API versions."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/v1"):
            response = await call_next(request)
            response.headers[
                "X-API-Warning"
            ] = "Version 1 of the API is deprecated and will be removed in the future."
            return response

        return await call_next(request)


def get_api_version(request: Request) -> str:
    """Returns the API version based on the request URL."""
    if request.url.path.startswith("/api/v2"):
        return "v2"
    return "v1"


def determine_version(request: Request) -> str:
    """Determines the API version based on headers or URL path."""
    version = request.headers.get("X-API-Version")
    if version:
        return version
    return get_api_version(request)
