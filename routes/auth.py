from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.jwt_manager import create_token
from schemas.user import User


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post('/login', tags=["auth"])
def login(user: User):
    if user.email == "cristian.duquew@gmail.com" and user.password == "NeverSettl3":
        token: str = create_token(user.dict())
        return JSONResponse(content={"token": token}, status_code=200)
    return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)
