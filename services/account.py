from models.account import Account
from schemas.account import AccountSchema


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
            self.db.commit()
            return account
        return None

    def subtract_balance(self, account_id, amount):
        account = self.db.query(Account).filter(
            Account.id == account_id).first()
        if account:
            current_balance = account.current_balance
            account.current_balance = current_balance - amount
            print(account.current_balance)
            self.db.commit()
            return account
        return None
