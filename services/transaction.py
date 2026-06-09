from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models.transaction import Transaction
from models.account import Account
from models.budget import Budget
from schemas.transaction import TransactionSchema, TransactionUpdateSchema
from utils.constants import TRANSACTION_TYPES


class TransactionService():

    # Constructor -> gets DB connection
    def __init__(self, db):
        self.db = db

    def read_transactions(self, filter: str):
        query = self.db.query(Transaction).options(
            joinedload(Transaction.from_account),
            joinedload(Transaction.to_account),
            joinedload(Transaction.budget),
            joinedload(Transaction.category),
        )

        # Filter by the current month
        if filter == 'this_month':
            print("entre al mes")
            start_of_month = datetime(
                datetime.now().year, datetime.now().month, 1).date()
            print("primer dia del mes", start_of_month)
            query = query.filter(
                Transaction.transaction_date >= start_of_month)

         # Filter by the current week
        elif filter == "this_week":
            print("entre a la semana")
            today = datetime.now().date()
            print("hoy", today)
            # Current week's Monday
            start_of_week = today - timedelta(days=today.weekday())
            print("lunes", start_of_week)
            query = query.filter(Transaction.transaction_date >= start_of_week)
            print("query", query)

        query = query.order_by(Transaction.transaction_date.desc())
        result = result = query.all()
        return result

    def _validate_transaction_payload(self, payload: dict):
        transaction_type = payload.get("type")
        amount = payload.get("amount")
        from_account_id = payload.get("from_account_id")
        to_account_id = payload.get("to_account_id")

        if amount is None or amount <= 0:
            raise ValueError("Transaction amount must be greater than 0")

        if transaction_type == TRANSACTION_TYPES['INCOME']:
            if not to_account_id:
                raise ValueError("INCOME transactions require a destination account")
        else:
            if not from_account_id:
                raise ValueError("This transaction type requires a source account")

        if from_account_id and to_account_id and from_account_id == to_account_id:
            raise ValueError("Source and destination accounts must be different")

    def _get_account(self, account_id: int):
        account = self.db.query(Account).filter(Account.id == account_id).first()

        if not account:
            raise ValueError(f"Account with id {account_id} was not found")

        return account

    def _get_budget(self, budget_id: int):
        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()

        if not budget:
            raise ValueError(f"Budget with id {budget_id} was not found")

        return budget

    def _increase_account_balance(self, account_id: int, amount: float):
        account = self._get_account(account_id)
        account.current_balance = (account.current_balance or 0) + amount
        account.last_transaction_date = datetime.now()

    def _decrease_account_balance(self, account_id: int, amount: float):
        account = self._get_account(account_id)
        current_balance = account.current_balance or 0
        next_balance = current_balance - amount

        if next_balance < 0:
            raise ValueError("Account balance cannot be negative")

        account.current_balance = next_balance
        account.last_transaction_date = datetime.now()

    def _apply_budget_effect(self, budget_id: int, amount: float):
        budget = self._get_budget(budget_id)
        spent_amount = budget.spent_amount or 0
        remaining_amount = budget.remaining_amount if budget.remaining_amount is not None else budget.amount
        next_remaining_amount = remaining_amount - amount

        if next_remaining_amount < 0:
            raise ValueError("Budget remaining amount cannot be negative")

        budget.remaining_amount = next_remaining_amount
        budget.spent_amount = spent_amount + amount
        budget.last_transaction_date = datetime.now()

    def _revert_budget_effect(self, budget_id: int, amount: float):
        budget = self._get_budget(budget_id)
        spent_amount = budget.spent_amount or 0

        if spent_amount - amount < 0:
            raise ValueError("Budget spent amount cannot be negative")

        remaining_amount = budget.remaining_amount if budget.remaining_amount is not None else budget.amount
        budget.remaining_amount = remaining_amount + amount
        budget.spent_amount = spent_amount - amount
        budget.last_transaction_date = datetime.now()

    def _apply_transaction_effects(self, transaction):
        if transaction.type == TRANSACTION_TYPES['INCOME']:
            self._increase_account_balance(transaction.to_account_id, transaction.amount)
            return

        self._decrease_account_balance(transaction.from_account_id, transaction.amount)

        if transaction.budget_id is not None:
            self._apply_budget_effect(transaction.budget_id, transaction.amount)

        if transaction.to_account_id is not None:
            self._increase_account_balance(transaction.to_account_id, transaction.amount)

    def _revert_transaction_effects(self, transaction):
        if transaction.type == TRANSACTION_TYPES['INCOME']:
            self._decrease_account_balance(transaction.to_account_id, transaction.amount)
            return

        self._increase_account_balance(transaction.from_account_id, transaction.amount)

        if transaction.budget_id is not None:
            self._revert_budget_effect(transaction.budget_id, transaction.amount)

        if transaction.to_account_id is not None:
            self._decrease_account_balance(transaction.to_account_id, transaction.amount)

    def _requires_balance_reconciliation(self, transaction, next_payload: dict):
        financial_fields = [
            "from_account_id",
            "to_account_id",
            "budget_id",
            "type",
            "amount",
        ]

        return any(
            getattr(transaction, field) != next_payload[field]
            for field in financial_fields
        )

    def create_transaction(self, transaction: TransactionSchema):
        new_transaction = Transaction(**transaction.dict())
        self._validate_transaction_payload({
            "from_account_id": new_transaction.from_account_id,
            "to_account_id": new_transaction.to_account_id,
            "budget_id": new_transaction.budget_id,
            "category_id": new_transaction.category_id,
            "type": new_transaction.type,
            "description": new_transaction.description,
            "title": new_transaction.title,
            "amount": new_transaction.amount,
            "icon": new_transaction.icon,
            "transaction_date": new_transaction.transaction_date,
        })

        try:
            self._apply_transaction_effects(new_transaction)
            self.db.add(new_transaction)
            self.db.commit()
            self.db.refresh(new_transaction)
            return new_transaction
        except Exception:
            self.db.rollback()
            raise

    def update_transaction(self, transaction_id: int, transaction: TransactionUpdateSchema):
        transaction_to_edit = self.db.query(Transaction).filter(
            Transaction.id == transaction_id).first()

        if not transaction_to_edit:
            return None

        update_data = transaction.model_dump(exclude_unset=True)

        next_payload = {
            "from_account_id": update_data.get("from_account_id", transaction_to_edit.from_account_id),
            "to_account_id": update_data.get("to_account_id", transaction_to_edit.to_account_id),
            "budget_id": update_data.get("budget_id", transaction_to_edit.budget_id),
            "category_id": update_data.get("category_id", transaction_to_edit.category_id),
            "type": update_data.get("type", transaction_to_edit.type),
            "description": update_data.get("description", transaction_to_edit.description),
            "title": update_data.get("title", transaction_to_edit.title),
            "amount": update_data.get("amount", transaction_to_edit.amount),
            "icon": update_data.get("icon", transaction_to_edit.icon),
            "transaction_date": update_data.get("transaction_date", transaction_to_edit.transaction_date),
        }

        self._validate_transaction_payload(next_payload)

        try:
            requires_reconciliation = self._requires_balance_reconciliation(
                transaction_to_edit, next_payload)

            if requires_reconciliation:
                self._revert_transaction_effects(transaction_to_edit)

            for field, value in next_payload.items():
                setattr(transaction_to_edit, field, value)

            if requires_reconciliation:
                self._apply_transaction_effects(transaction_to_edit)

            self.db.commit()
            self.db.refresh(transaction_to_edit)
            return transaction_to_edit
        except Exception:
            self.db.rollback()
            raise
