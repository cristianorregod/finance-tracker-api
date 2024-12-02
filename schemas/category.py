from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class CategorySchema(BaseModel):
    id: Optional[int] = Field(
        None, description="The unique identifier of the category")
    name: str = Field(min_length=3, max_length=25,
                      description="The name of the category")
    description: Optional[str] = Field(
        None, description="The description of the category")
    icon: Optional[str] = Field(
        None, description="The icon of the category")

    class Config:
        orm_mode = True
