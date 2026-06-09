from fastapi import APIRouter, Depends, HTTPException
from models.budget import Budget
from schemas.budget import BudgetSchema, BudgetUpdateSchema
from config.database import Session
from typing import List
from services.budget import BudgetService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from middlewares.jwt_bearer import JWTBearer


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
    new_budget = BudgetService(db).create_budget(budget).to_dict()
    db.close()
    return JSONResponse(content={"message": "Budget created successfully", "budget": jsonable_encoder(new_budget)}, status_code=201)


@budget_router.patch("/{budget_id}", tags=["budgets"], response_model=dict, dependencies=[Depends(JWTBearer())])
def update_budget(budget_id: int, budget: BudgetUpdateSchema) -> dict:
    db = Session()

    try:
        updated_budget = BudgetService(db).update_budget(budget_id, budget)

        if updated_budget is None:
            raise HTTPException(status_code=404, detail="Budget not found")

        return JSONResponse(
            content={
                "message": "Budget updated successfully",
                "budget": jsonable_encoder(updated_budget.to_dict())
            },
            status_code=200
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        db.close()
