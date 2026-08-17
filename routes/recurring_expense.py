from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from config.database import Session
from middlewares.jwt_bearer import JWTBearer
from schemas.recurring_expense import (
    RecurringExpenseConfirmSchema, RecurringExpenseCreateSchema,
    RecurringExpenseSchema, RecurringExpenseUpdateSchema,
)
from services.recurring_expense import RecurringExpenseService

recurring_expense_router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"], dependencies=[Depends(JWTBearer())])


def _response(expense, message=""):
    return JSONResponse(content={"message": message, "recurring_expense": jsonable_encoder(expense.to_dict())} if message else jsonable_encoder(expense.to_dict()))


@recurring_expense_router.get("/", response_model=list[RecurringExpenseSchema])
def list_recurring_expenses():
    db = Session()
    try:
        return [_expense.to_dict() for _expense in RecurringExpenseService(db).list()]
    finally:
        db.close()


@recurring_expense_router.get("/{expense_id}", response_model=RecurringExpenseSchema)
def get_recurring_expense(expense_id: int):
    db = Session()
    try:
        expense = RecurringExpenseService(db).get(expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Recurring expense not found")
        return expense.to_dict()
    finally:
        db.close()


@recurring_expense_router.post("/", status_code=201, response_model=dict)
def create_recurring_expense(payload: RecurringExpenseCreateSchema):
    db = Session()
    try:
        return _response(RecurringExpenseService(db).create(payload), "Recurring expense created successfully")
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        db.close()


@recurring_expense_router.patch("/{expense_id}", response_model=dict)
def update_recurring_expense(expense_id: int, payload: RecurringExpenseUpdateSchema):
    db = Session()
    try:
        expense = RecurringExpenseService(db).update(expense_id, payload)
        if not expense:
            raise HTTPException(status_code=404, detail="Recurring expense not found")
        return _response(expense, "Recurring expense updated successfully")
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        db.close()


@recurring_expense_router.delete("/{expense_id}", status_code=204)
def delete_recurring_expense(expense_id: int):
    db = Session()
    try:
        expense = RecurringExpenseService(db).get(expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Recurring expense not found")
        if expense.transactions:
            raise HTTPException(status_code=400, detail="Recurring expenses with confirmed transactions cannot be deleted")
        db.delete(expense)
        db.commit()
    finally:
        db.close()


def _status(expense_id, status):
    db = Session()
    try:
        expense = RecurringExpenseService(db).set_status(expense_id, status)
        if not expense:
            raise HTTPException(status_code=404, detail="Recurring expense not found")
        return _response(expense, f"Recurring expense {status} successfully")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        db.close()


@recurring_expense_router.post("/{expense_id}/pause", response_model=dict)
def pause_recurring_expense(expense_id: int):
    return _status(expense_id, "paused")


@recurring_expense_router.post("/{expense_id}/resume", response_model=dict)
def resume_recurring_expense(expense_id: int):
    return _status(expense_id, "active")


@recurring_expense_router.post("/{expense_id}/cancel", response_model=dict)
def cancel_recurring_expense(expense_id: int):
    return _status(expense_id, "cancelled")


@recurring_expense_router.post("/{expense_id}/confirm", response_model=dict)
def confirm_recurring_expense(expense_id: int, payload: RecurringExpenseConfirmSchema | None = None):
    db = Session()
    try:
        result = RecurringExpenseService(db).confirm(expense_id, payload or RecurringExpenseConfirmSchema())
        if result is None:
            raise HTTPException(status_code=404, detail="Recurring expense not found")
        transaction, expense = result
        return JSONResponse(content={"message": "Recurring expense confirmed successfully", "transaction": jsonable_encoder(transaction.to_dict()), "recurring_expense": jsonable_encoder(expense.to_dict())})
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        db.close()
