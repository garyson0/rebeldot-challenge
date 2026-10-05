import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

# auto_error=False so we can return our 401 response when the header is missing.
bearer_scheme = HTTPBearer(auto_error=False)


def get_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    """Check the API token sent by the client; raise 401 if it is missing or wrong."""
    expected_token = settings.api_token.get_secret_value()

    if credentials is None or not expected_token:
        raise HTTPException(status_code=401, detail="Missing or invalid API token")

    if not secrets.compare_digest(credentials.credentials, expected_token):
        raise HTTPException(status_code=401, detail="Missing or invalid API token")
    return credentials.credentials
