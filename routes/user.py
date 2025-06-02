from fastapi import APIRouter
from schemas.user import UserSchema
from config.database import Session
from services.user import UserService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/", tags=["users"], status_code=201, response_model=dict)
def create_user(user: UserSchema) -> dict:
    db = Session()
    created_user = UserService(db).create_user(user).to_dict()
    db.close()
    return JSONResponse(content={"message": "User created successfully", "user": jsonable_encoder(created_user)}, status_code=201)
