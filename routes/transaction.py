from fastapi import APIRouter, Depends, HTTPException, Query
from models.transaction import Transaction
from schemas.transaction import TransactionSchema, TransactionUpdateSchema
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


@transaction_router.patch("/{transaction_id}", tags=["transactions"], response_model=dict, dependencies=[Depends(JWTBearer())])
def update_transaction(transaction_id: int, transaction: TransactionUpdateSchema) -> dict:
    db = Session()

    try:
        updated_transaction = TransactionService(db).update_transaction(transaction_id, transaction)

        if updated_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return JSONResponse(
            content={
                "message": "Transaction updated successfully",
                "transaction": jsonable_encoder(updated_transaction.to_dict())
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
