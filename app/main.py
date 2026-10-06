import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import ask, health
from app.core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(health.router)
app.include_router(ask.router)


@app.exception_handler(ServiceUnavailableError)
async def service_unavailable_handler(request: Request, error: ServiceUnavailableError):
    logger.exception("Service unavailable: %s", error)
    return JSONResponse(
        status_code=503,
        content={"detail": "The assistant is temporarily unavailable, please try again later."},
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, error: Exception):
    logger.exception("Unexpected error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
