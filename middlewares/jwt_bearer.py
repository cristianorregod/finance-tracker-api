from fastapi.security import HTTPBearer
from utils.jwt_manager import validate_token
from fastapi import Request, HTTPException


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        is_valid = validate_token(auth.credentials)
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid token")
