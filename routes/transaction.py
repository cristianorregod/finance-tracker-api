from fastapi import APIRouter, Depends, Path, Query
from models.transaction import Transaction
from schemas.transaction import TransactionSchema
from typing import List, Optional
from config.database import Session
from services.transaction import TransactionService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from middlewares.jwt_bearer import JWTBearer

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transaction_router.get("/", tags=["transactions"], response_model=List[TransactionSchema], dependencies=[Depends(JWTBearer())])
def get_transactions(filter: Optional[str] = Query("all", enum=["this_month", "this_week", "all"])) -> List[Transaction]:
    db = Session()
    data = TransactionService(db).read_transactions(filter)
    db.close()
    transactions = [transaction.to_dict() for transaction in data]
    return JSONResponse(content=jsonable_encoder(transactions), status_code=200)


@transaction_router.post("/", tags=["transactions"], status_code=201, response_model=dict, dependencies=[Depends(JWTBearer())])
def create_transaction(transaction: TransactionSchema) -> dict:
    db = Session()
    createdTransaction = TransactionService(
        db).create_transaction(transaction).to_dict()
    db.close()
    return JSONResponse(content={"message": "Transaction created successfully", "transaction": jsonable_encoder(createdTransaction)}, status_code=201)
