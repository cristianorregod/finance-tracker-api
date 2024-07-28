from fastapi import APIRouter, Depends, Path, Query
from models.transaction import Transaction
from schemas.transaction import TransactionSchema
from typing import List
from config.database import Session
from services.transaction import TransactionService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transaction_router.get("/", tags=["transactions"], response_model=List[TransactionSchema])
def get_accounts() -> List[Transaction]:
    db = Session()
    data = TransactionService(db).read_transactions()
    db.close()
    return JSONResponse(content=jsonable_encoder(data), status_code=200)


@transaction_router.post("/", tags=["transactions"], status_code=201, response_model=dict)
def create_account(transaction: TransactionSchema) -> dict:
    db = Session()
    TransactionService(db).create_transaction(transaction)
    db.close()
    return JSONResponse(content={"message": "Transaction created successfully"}, status_code=201)