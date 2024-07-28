from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.test import Test
from sqlalchemy import select
from config.database import Session, Base, engine
from routes.account import account_router
from routes.budget import budget_router
from routes.transaction import transaction_router


load_dotenv()
# Create tables if they don't exist already
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.title = "Finance Tracker API"
app.version = "0.0.1"

app.include_router(account_router)
app.include_router(budget_router)
app.include_router(transaction_router)


@app.get("/test")
def get_test():
    db = Session()
    result = db.query(Test).all()
    return JSONResponse(content=jsonable_encoder(result))
