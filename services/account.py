from datetime import datetime
from models.account import Account
from models.transaction import Transaction
from schemas.account import AccountSchema
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
        print("consultando")
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
        print("transactions", transactions)
        #transactions = [jsonable_encoder(transaction) for transaction in transactions]
        transactions = [transaction.to_dict() for transaction in transactions]
        account = account.to_dict()
        account["transactions"] = transactions
       
        return account
