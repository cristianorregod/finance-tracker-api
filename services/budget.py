from datetime import datetime
from models.budget import Budget
from schemas.budget import BudgetSchema, BudgetUpdateSchema


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

    def update_budget(self, id: int, budget: BudgetUpdateSchema):
        prev_budget = self.db.query(Budget).filter(Budget.id == id).first()
        if prev_budget:
            update_data = budget.model_dump(exclude_unset=True)

            if "amount" in update_data:
                new_amount = update_data["amount"]
                spent_amount = prev_budget.spent_amount or 0

                if spent_amount > new_amount:
                    raise ValueError(
                        "Budget amount cannot be lower than the amount already spent"
                    )

                prev_budget.amount = new_amount
                prev_budget.remaining_amount = new_amount - spent_amount

            if "name" in update_data:
                prev_budget.name = update_data["name"]
            if "description" in update_data:
                prev_budget.description = update_data["description"]
            if "icon" in update_data:
                prev_budget.icon = update_data["icon"]

            self.db.commit()
            self.db.refresh(prev_budget)
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
