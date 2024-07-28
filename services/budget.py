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
