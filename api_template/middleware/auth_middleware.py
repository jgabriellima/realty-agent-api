from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api_template.api.v1.auth.auth import get_current_user

security = HTTPBearer()


async def auth_middleware(request: Request, credentials: HTTPAuthorizationCredentials = security):
    try:
        token = credentials.credentials
        user = await get_current_user(token)
        request.state.user = user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
