from fastapi import APIRouter
from models.budget import Budget
from schemas.budget import BudgetSchema
from config.database import Session
from typing import List
from services.budget import BudgetService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


budget_router = APIRouter(prefix="/budgets", tags=["budgets"])


@budget_router.get("/", tags=["budgets"], response_model=List[BudgetSchema])
def get_accounts() -> List[Budget]:
    db = Session()
    data = BudgetService(db).read_budgets()
    db.close()
    return JSONResponse(content=jsonable_encoder(data), status_code=200)


@budget_router.post("/", tags=["budgets"], response_model=BudgetSchema)
def create_budget(budget: BudgetSchema) -> dict:
    db = Session()
    new_budget = BudgetService(db).create_budget(budget)
    db.close()
    return JSONResponse(content={"message": "Budget created successfully"}, status_code=201)
