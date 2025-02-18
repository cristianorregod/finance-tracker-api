from fastapi import APIRouter, Depends
from typing import List
from config.database import Session
from services.parameters import ParametersService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from middlewares.jwt_bearer import JWTBearer


parameter_router = APIRouter(prefix="/parameters", tags=["parameters"])


@parameter_router.get("/", tags=["parameters"], response_model=List[dict], dependencies=[Depends(JWTBearer())])
def get_initial_data() -> List[dict]:
    db = Session()
    data = ParametersService(db).get_initial_data()
    db.close()
    return JSONResponse(content=jsonable_encoder(data), status_code=200)
