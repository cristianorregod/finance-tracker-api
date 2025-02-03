from datetime import datetime
from models.budget import Budget
from schemas.budget import BudgetSchema


class BudgetService():

    # Constructor -> gets DB connection
    def __init__(self, db):
        self.db = db

    def read_budgets(self):
        result = self.db.query(Budget).all()
        return result

    def create_budget(self, budget: BudgetSchema):
        new_budget = Budget(**budget.dict())
        self.db.add(new_budget)
        self.db.commit()
        return new_budget

    def update_budget(self, id: int, budget: BudgetSchema):
        prev_budget = self.db.query(Budget).filter(Budget.id == id).first()
        if prev_budget:
            prev_budget.name = budget.name
            prev_budget.description = budget.description
            prev_budget.amount = budget.amount
            prev_budget.icon = budget.icon
            self.db.commit()
            return prev_budget
        return None

    def update_balance(self, id: int, amount: float):
        prev_budget = self.db.query(Budget).filter(Budget.id == id).first()
        if prev_budget:
            prev_budget.remaining_amount = prev_budget.remaining_amount - amount
            prev_budget.spent_amount = prev_budget.spent_amount + amount
            prev_budget.last_transaction_date = datetime.now()
            self.db.commit()
            return prev_budget
        return None
