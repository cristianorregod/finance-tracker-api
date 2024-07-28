from models.transaction import Transaction
from schemas.transaction import TransactionSchema


class TransactionService():

    # Constructor -> gets DB connection
    def __init__(self, db):
        self.db = db

    def read_transactions(self):
        result = self.db.query(Transaction).all()
        return result

    def create_transaction(self, account: TransactionSchema):
        new_account = Transaction(**account.dict())
        self.db.add(new_account)
        self.db.commit()
        return new_account
