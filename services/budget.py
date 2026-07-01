from datetime import datetime
from models.budget import Budget
from schemas.budget import BudgetSchema, BudgetUpdateSchema
from services.budget_cycle import BudgetCycleService


class BudgetService():

    # Constructor -> gets DB connection
    def __init__(self, db):
        self.db = db
        self.cycle_service = BudgetCycleService(db)

    def _serialize_budget(self, budget: Budget, reference_date=None):
        cycle = self.cycle_service.sync_budget_snapshot(budget, reference_date)
        budget_dict = budget.to_dict()
        budget_dict["active_cycle"] = cycle.to_dict() if cycle else None
        return budget_dict

    def read_budgets(self):
        result = self.db.query(Budget).all()
        serialized_budgets = [self._serialize_budget(budget) for budget in result]
        self.db.commit()
        return serialized_budgets

    def serialize_budget(self, budget: Budget, reference_date=None):
        serialized_budget = self._serialize_budget(budget, reference_date)
        self.db.commit()
        self.db.refresh(budget)
        return serialized_budget

    def create_budget(self, budget: BudgetSchema):
        budget_payload = budget.model_dump()
        budget_payload["period_type"] = budget_payload.get("period_type") or "monthly"
        budget_payload["spent_amount"] = 0
        budget_payload["remaining_amount"] = budget_payload.get("amount", 0)
        new_budget = Budget(**budget_payload)
        self.db.add(new_budget)
        self.db.flush()
        self.cycle_service.get_or_create_cycle(new_budget, datetime.now().date())
        self.cycle_service.sync_budget_snapshot(new_budget)
        self.db.commit()
        self.db.refresh(new_budget)
        return new_budget

    def update_budget(self, id: int, budget: BudgetUpdateSchema):
        prev_budget = self.db.query(Budget).filter(Budget.id == id).first()
        if prev_budget:
            update_data = budget.model_dump(exclude_unset=True)

            if "amount" in update_data:
                new_amount = update_data["amount"]
                current_cycle = self.cycle_service.get_or_create_cycle(prev_budget, datetime.now().date())
                spent_amount = current_cycle.spent_amount or 0

                if spent_amount > new_amount:
                    raise ValueError(
                        "Budget amount cannot be lower than the amount already spent"
                    )

                prev_budget.amount = new_amount
                current_cycle.limit_amount = new_amount
                current_cycle.remaining_amount = new_amount - spent_amount

            if "period_type" in update_data:
                prev_budget.period_type = update_data["period_type"]

            if "name" in update_data:
                prev_budget.name = update_data["name"]
            if "description" in update_data:
                prev_budget.description = update_data["description"]
            if "icon" in update_data:
                prev_budget.icon = update_data["icon"]

            self.cycle_service.sync_budget_snapshot(prev_budget)
            self.db.commit()
            self.db.refresh(prev_budget)
            return prev_budget
        return None
