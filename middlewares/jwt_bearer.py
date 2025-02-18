from fastapi.security import HTTPBearer
from utils.jwt_manager import validate_token
from fastapi import Request, HTTPException


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        print("credentials", auth.credentials)
        print("iniciando validacion de token")
        is_valid = validate_token(auth.credentials)
        print("is_valid", is_valid)
        if is_valid.get('error'):
            raise HTTPException(status_code=403, detail=is_valid['error'])
