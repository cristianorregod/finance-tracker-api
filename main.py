from dotenv import load_dotenv
from fastapi import FastAPI
from config.database import Session, Base, engine
from routes.account import account_router
from routes.budget import budget_router
from routes.transaction import transaction_router
from routes.category import category_router
from middlewares.error_handler import ErrorHandler


load_dotenv()
# Create tables if they don't exist already
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.title = "Finance Tracker API"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)
app.include_router(account_router)
app.include_router(budget_router)
app.include_router(category_router)
app.include_router(transaction_router)
