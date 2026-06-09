from datetime import datetime
from models.account import Account
from models.transaction import Transaction
from schemas.account import AccountSchema, AccountUpdateSchema
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, desc
from fastapi.encoders import jsonable_encoder

class AccountService():

    # Constructor -> gets DB connection
    def __init__(self, db):
        self.db = db

    def read_accounts(self):
        result = self.db.query(Account).all()
        return result

    def create_account(self, account: AccountSchema):
        new_account = Account(**account.dict())
        self.db.add(new_account)
        self.db.commit()
        return new_account

    def update_account(self, account_id: int, account: AccountUpdateSchema):
        prev_account = self.db.query(Account).filter(Account.id == account_id).first()

        if not prev_account:
            return None

        update_data = account.model_dump(exclude_unset=True)

        if "initial_balance" in update_data:
            has_transactions = self.db.query(Transaction).filter(
                or_(
                    Transaction.from_account_id == account_id,
                    Transaction.to_account_id == account_id,
                )
            ).first()

            if has_transactions:
                raise ValueError(
                    "Initial balance cannot be edited once the account has transactions"
                )

            prev_account.initial_balance = update_data["initial_balance"]
            prev_account.current_balance = update_data["initial_balance"]

        if "name" in update_data:
            prev_account.name = update_data["name"]
        if "account_type" in update_data:
            prev_account.account_type = update_data["account_type"]
        if "icon" in update_data:
            prev_account.icon = update_data["icon"]

        self.db.commit()
        self.db.refresh(prev_account)
        return prev_account

    def add_balance(self, account_id, amount):
        account = self.db.query(Account).filter(
            Account.id == account_id).first()
        if account:
            current_balance = account.current_balance
            account.current_balance = current_balance + amount
            account.last_transaction_date = datetime.now()
            self.db.commit()
            return account
        return None

    def subtract_balance(self, account_id, amount):
        account = self.db.query(Account).filter(
            Account.id == account_id).first()
        if account:
            current_balance = account.current_balance
            account.current_balance = current_balance - amount
            account.last_transaction_date = datetime.now()
            print(account.current_balance)
            self.db.commit()
            return account
        return None
    
    def get_account_by_id(self, account_id):
        account = self.db.query(Account).options(
            joinedload(Account.from_transactions),
            joinedload(Account.to_transactions)    # Cargar transacciones de entrada
        ).filter(
            Account.id == account_id).first()
        if account is None:
            return None

        transactions = self.db.query(Transaction).options(
                joinedload(Transaction.from_account),
                joinedload(Transaction.to_account),
                joinedload(Transaction.budget),
                joinedload(Transaction.category),
            ).filter(
                or_(
                    Transaction.from_account_id == account_id,
                    Transaction.to_account_id == account_id
                )
            ).order_by(desc(Transaction.transaction_date)).all()
        transactions = [transaction.to_dict() for transaction in transactions]
        account = account.to_dict()
        account["transactions"] = transactions
       
        return account
