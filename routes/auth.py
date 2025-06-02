from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from utils.jwt_manager import create_token
from schemas.user import UserLoginSchema
from config.database import Session
from services.user import UserService
from utils.password_manager import PasswordManager
from sqlalchemy.exc import SQLAlchemyError



auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post('/login', tags=["auth"])
def login(user: UserLoginSchema):
    try:
        db = Session()
        user_db = UserService(db).get_user_by_email(user.email)
        
        if not user_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        user_dict = user_db.to_dict()
        password_manager = PasswordManager()
        
        if not password_manager.check_password(user.password, user_dict["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        token: str = create_token({"email": user_dict['email'], "role": user_dict['role']})
        return JSONResponse(
            content={
                "token": token,
                "email": user_dict['email'],
                "role": user_dict['role']
            },
            status_code=200
        )
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        db.close()

