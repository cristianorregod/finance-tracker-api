from fastapi import APIRouter, Depends, HTTPException
from models.account import Account
from schemas.account import AccountSchema, AccountUpdateSchema
from typing import List
from config.database import Session
from services.account import AccountService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from middlewares.jwt_bearer import JWTBearer
from sqlalchemy.exc import SQLAlchemyError

account_router = APIRouter(prefix="/accounts", tags=["accounts"])


@account_router.get("/", tags=["accounts"], response_model=List[AccountSchema], dependencies=[Depends(JWTBearer())])
def get_accounts() -> List[Account]:
    db = Session()
    data = AccountService(db).read_accounts()
    db.close()
    return JSONResponse(content=jsonable_encoder(data), status_code=200)


@account_router.post("/", tags=["accounts"], status_code=201, response_model=dict)
def create_account(account: AccountSchema) -> dict:
    db = Session()
    creatdAccount = AccountService(db).create_account(account).to_dict()

    db.close()
    return JSONResponse(content={"message": "Account created successfully", "account": jsonable_encoder(creatdAccount)}, status_code=201)


@account_router.get("/{account_id}", tags=["accounts"], response_model=AccountSchema, dependencies=[Depends(JWTBearer())])
def get_account_by_id(account_id: int) -> Account:
    db = Session()

    try:
        account = AccountService(db).get_account_by_id(account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return JSONResponse(content=jsonable_encoder(account), status_code=200)
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        db.close()


@account_router.patch("/{account_id}", tags=["accounts"], response_model=dict, dependencies=[Depends(JWTBearer())])
def update_account(account_id: int, account: AccountUpdateSchema) -> dict:
    db = Session()

    try:
        updated_account = AccountService(db).update_account(account_id, account)

        if updated_account is None:
            raise HTTPException(status_code=404, detail="Account not found")

        return JSONResponse(
            content={
                "message": "Account updated successfully",
                "account": jsonable_encoder(updated_account.to_dict())
            },
            status_code=200
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        db.close()
