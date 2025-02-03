from models.account import Account
from models.budget import Budget
from models.transaction import Transaction
from models.category import Category


class ParametersService():
    def __init__(self, db):
        self.db = db

    def get_initial_data(self):
        accounts = self.db.query(Account).all()
        budgets = self.db.query(Budget).all()
        transactions = self.db.query(Transaction).order_by(
            Transaction.transaction_date.desc()).all()
        categories = self.db.query(Category).all()
        transactions = [transaction.to_dict() for transaction in transactions]
        result = {"accounts": accounts, "budgets": budgets,
                  "transactions": transactions, "categories": categories}
        print("result", result)
        return result
