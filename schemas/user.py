from pydantic import BaseModel, Field
from typing import Optional

class UserSchema(BaseModel):
    name: str = Field(min_length=3, max_length=25,
                      description="The name of the user")
    email: str = Field(min_length=5, max_length=25,
                      description="The email of the user")
    password: str = Field(min_length=3, max_length=25,
                      description="The password of the user")
    role: str = Field(min_length=3, max_length=25,
                      description="The role of the user")
    
    class Config:
        orm_mode = True

class UserLoginSchema(BaseModel):
    email: str = Field(min_length=5, max_length=25,
                      description="The email of the user")
    password: str = Field(min_length=3, max_length=25,
                      description="The password of the user")
    
    
