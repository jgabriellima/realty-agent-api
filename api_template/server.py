import datetime
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from http import HTTPStatus
from starlette.requests import Request
from starlette.responses import JSONResponse

from api_template.api.common.api_exceptions import BaseAPIException
from api_template.api.v1 import router
from api_template.config.settings import settings
from api_template.middleware.ratelimit_middleware import RateLimitMiddleware
from api_template.middleware.request_middleware import RequestContextLogMiddleware
from api_template.middleware.security_headers_middleware import SecurityHeadersMiddleware
from api_template.queue.setup import lifespan_handler

load_dotenv()

app = FastAPI(**settings.api_description, lifespan=lifespan_handler)

# Set up logging
logger = logging.getLogger(__name__)

app.include_router(router.router)
app.add_middleware(RequestContextLogMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
    period=settings.RATE_LIMIT_PERIOD,
    hash_ips=settings.HASH_IPS,
)

whitelist_paths = ["/docs", "/redoc", "/openapi.json"]
app.add_middleware(SecurityHeadersMiddleware)


@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    logger.error(f"API Exception: {exc.error_code}, Message: {exc.error_msg}")
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.get("/", tags=["Base"])
async def root():
    return {"message": "API Template!", "datetime": datetime.datetime.now()}
