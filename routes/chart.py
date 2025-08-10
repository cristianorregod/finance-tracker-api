from fastapi import APIRouter, Depends, Path, Query
from config.database import Session
from services.chart import ChartService
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer

chart_router = APIRouter(prefix="/charts", tags=["charts"])

@chart_router.get("/monthly-income-expense", tags=["charts"], dependencies=[Depends(JWTBearer())])
def get_test_chart():
    db = Session()
    data = ChartService(db).get_income_expense_chart()
    db.close()
    return JSONResponse(content={"type": "bar", "data":data}, status_code=200)

@chart_router.get("/expense-by-category", tags=["charts"], dependencies=[Depends(JWTBearer())])
def get_expense_by_category_chart():
    db = Session()
    data = ChartService(db).get_expense_by_category_chart()
    db.close()
    return JSONResponse(content={"type": "pie", "data":data}, status_code=200)

