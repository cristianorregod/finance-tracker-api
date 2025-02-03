from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models.transaction import Transaction
from schemas.transaction import TransactionSchema
from services.account import AccountService
from services.budget import BudgetService
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

    def create_transaction(self, transaction: TransactionSchema):
        new_transaction = Transaction(**transaction.dict())
        print("new_transaction", new_transaction)
        if new_transaction.type == TRANSACTION_TYPES.INCOME:
            account_id = new_transaction.to_account_id
            print('Consultar to_account_id para actualizar saldo')
            add_balance = AccountService(self.db).add_balance(
                account_id, new_transaction.amount)
            print("Add balance", add_balance)
        else:
            print('Consultar from_account_id para actualizar saldo')
            account_id = new_transaction.from_account_id
            if new_transaction.budget_id:
                print('Consultar budget_id para actualizar saldo')
                budget_id = new_transaction.budget_id
                update_budget_balance = BudgetService(
                    self.db).update_balance(budget_id, new_transaction.amount)
                print("Update budget balance", update_budget_balance)
            subtract_balance = AccountService(self.db).subtract_balance(
                account_id, new_transaction.amount)
            print("Subtract balance", subtract_balance)
            if new_transaction.to_account:
                add_balance = AccountService(self.db).add_balance(
                    new_transaction.to_account_id, new_transaction.amount)
        print(new_transaction.amount)
        self.db.add(new_transaction)
        self.db.commit()
        return new_transaction
