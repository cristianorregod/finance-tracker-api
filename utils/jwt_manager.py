from datetime import datetime, timedelta
import os
from jwt import encode, decode
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token: str = encode(payload=to_encode,
                        key=JWT_SECRET_KEY, algorithm="HS256")
    return token


def validate_token(token: str):
    data: dict = decode(token, key=JWT_SECRET_KEY, algorithms=["HS256"])
    return data
