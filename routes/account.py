from fastapi import APIRouter, Depends, Path, Query
from models.account import Account
from schemas.account import AccountSchema
from typing import List
from config.database import Session
from services.account import AccountService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from middlewares.jwt_bearer import JWTBearer

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
