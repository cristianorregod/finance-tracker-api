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
