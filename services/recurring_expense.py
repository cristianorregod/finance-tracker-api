from calendar import monthrange
from datetime import date
from sqlalchemy.exc import IntegrityError
from models.account import Account
from models.budget import Budget
from models.category import Category
from models.recurring_expense import RecurringExpense
from models.transaction import Transaction
from schemas.recurring_expense import (
    RecurringExpenseConfirmSchema, RecurringExpenseCreateSchema, RecurringExpenseUpdateSchema,
)
from schemas.transaction import TransactionSchema
from services.transaction import TransactionService


class RecurringExpenseService:
    STATUSES = {"active", "paused", "cancelled"}

    def __init__(self, db):
        self.db = db

    @staticmethod
    def occurrence_for(year, month, day):
        return date(year, month, min(day, monthrange(year, month)[1]))

    @staticmethod
    def next_month(value, day):
        year, month = value.year, value.month + 1
        if month == 13:
            year, month = year + 1, 1
        return RecurringExpenseService.occurrence_for(year, month, day)

    @staticmethod
    def first_occurrence(start_date, day):
        occurrence = RecurringExpenseService.occurrence_for(
            start_date.year, start_date.month, day)
        if occurrence < start_date:
            occurrence = RecurringExpenseService.next_month(occurrence, day)
        return occurrence

    def _validate_references(self, payload):
        if not self.db.query(Account).filter(Account.id == payload["account_id"]).first():
            raise ValueError("Account was not found")
        for model, key, label in ((Budget, "budget_id", "Budget"), (Category, "category_id", "Category")):
            if payload.get(key) is not None and not self.db.query(model).filter(model.id == payload[key]).first():
                raise ValueError(f"{label} was not found")

    def create(self, payload: RecurringExpenseCreateSchema):
        data = payload.model_dump()
        self._validate_references(data)
        data["next_occurrence_date"] = self.first_occurrence(
            data["start_date"], data["day_of_month"])
        expense = RecurringExpense(**data)
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def list(self):
        return self.db.query(RecurringExpense).order_by(RecurringExpense.next_occurrence_date).all()

    def get(self, expense_id):
        return self.db.query(RecurringExpense).filter(RecurringExpense.id == expense_id).first()

    def update(self, expense_id, payload: RecurringExpenseUpdateSchema):
        expense = self.get(expense_id)
        if not expense:
            return None
        data = payload.model_dump(exclude_unset=True)
        values = {**{column.name: getattr(expense, column.name) for column in expense.__table__.columns}, **data}
        self._validate_references(values)
        if values["end_date"] and values["end_date"] < values["start_date"]:
            raise ValueError("end_date cannot be earlier than start_date")
        for key, value in data.items():
            setattr(expense, key, value)
        if any(key in data for key in ("day_of_month", "start_date")) and not expense.last_confirmed_date:
            expense.next_occurrence_date = self.first_occurrence(
                expense.start_date, expense.day_of_month)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def set_status(self, expense_id, status):
        if status not in self.STATUSES:
            raise ValueError("Unsupported recurring expense status")
        expense = self.get(expense_id)
        if not expense:
            return None
        expense.status = status
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def confirm(self, expense_id, payload: RecurringExpenseConfirmSchema):
        expense = self.get(expense_id)
        if not expense:
            return None
        if expense.status != "active":
            raise ValueError("Only active recurring expenses can be confirmed")
        confirmation_date = payload.transaction_date or date.today()
        if confirmation_date < expense.next_occurrence_date:
            raise ValueError("Recurring expense occurrence is not due yet")
        if expense.end_date and expense.next_occurrence_date > expense.end_date:
            raise ValueError("Recurring expense has ended")
        period = expense.next_occurrence_date.strftime("%Y-%m")
        if self.db.query(Transaction).filter(
            Transaction.recurring_expense_id == expense.id,
            Transaction.occurrence_period == period,
        ).first():
            raise ValueError("This recurring expense occurrence was already confirmed")

        transaction_title = payload.title or expense.name
        if len(transaction_title) < 15:
            transaction_title = f"{transaction_title} expense"
        transaction_title = transaction_title[:25]
        transaction = TransactionSchema(
            from_account_id=expense.account_id,
            budget_id=expense.budget_id,
            category_id=expense.category_id,
            type="expense",
            description=payload.description if payload.description is not None else expense.description,
            title=transaction_title,
            amount=expense.amount,
            transaction_date=confirmation_date,
            icon=payload.icon,
            recurring_expense_id=expense.id,
            occurrence_period=period,
        )
        try:
            created = TransactionService(self.db).create_transaction(transaction, commit=False)
            expense.last_confirmed_date = expense.next_occurrence_date
            expense.next_occurrence_date = self.next_month(expense.next_occurrence_date, expense.day_of_month)
            if expense.end_date and expense.next_occurrence_date > expense.end_date:
                expense.status = "cancelled"
            self.db.commit()
            self.db.refresh(created)
            self.db.refresh(expense)
            return created, expense
        except IntegrityError:
            self.db.rollback()
            raise ValueError("This recurring expense occurrence was already confirmed")
        except Exception:
            self.db.rollback()
            raise
