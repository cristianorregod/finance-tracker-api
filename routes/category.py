from fastapi import APIRouter
from models.category import Category
from schemas.category import CategorySchema
from services.category import CategoryService
from typing import List
from config.database import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

category_router = APIRouter(prefix="/categories", tags=["categories"])


@category_router.get("/", tags=["categories"], response_model=List[CategorySchema])
def get_categories() -> List[Category]:
    db = Session()
    data = CategoryService(db).get_categories()
    db.close()
    return JSONResponse(content=jsonable_encoder(data), status_code=200)


@category_router.post("/", tags=["categories"], response_model=CategorySchema)
def create_category(category: CategorySchema) -> dict:
    db = Session()
    CategoryService(db).create_category(category)
    db.close()
    return JSONResponse(content={"message": "Category created successfully"}, status_code=201)
