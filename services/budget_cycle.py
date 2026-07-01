from calendar import monthrange
from datetime import date, datetime
from sqlalchemy import and_, or_
from models.budget import Budget
from models.budget_cycle import BudgetCycle


class BudgetCycleService:
    DEFAULT_PERIOD_TYPE = 'monthly'

    def __init__(self, db):
        self.db = db

    def get_cycle_range(self, reference_date: date, period_type: str):
        normalized_period_type = period_type or self.DEFAULT_PERIOD_TYPE

        if normalized_period_type != self.DEFAULT_PERIOD_TYPE:
            raise ValueError(f"Unsupported budget period type: {normalized_period_type}")

        start_date = reference_date.replace(day=1)
        end_date = reference_date.replace(day=monthrange(reference_date.year, reference_date.month)[1])
        return start_date, end_date

    def get_cycle_by_date(self, budget_id: int, reference_date: date):
        return self.db.query(BudgetCycle).filter(
            BudgetCycle.budget_id == budget_id,
            BudgetCycle.start_date <= reference_date,
            BudgetCycle.end_date >= reference_date,
        ).first()

    def get_or_create_cycle(self, budget: Budget, reference_date: date):
        cycle = self.get_cycle_by_date(budget.id, reference_date)

        if cycle:
            return cycle

        start_date, end_date = self.get_cycle_range(reference_date, budget.period_type)

        existing_cycle = self.db.query(BudgetCycle).filter(
            BudgetCycle.budget_id == budget.id,
            BudgetCycle.start_date == start_date,
            BudgetCycle.end_date == end_date,
        ).first()

        if existing_cycle:
            return existing_cycle

        self.close_overlapping_cycles(budget.id, start_date, end_date)

        new_cycle = BudgetCycle(
            budget_id=budget.id,
            start_date=start_date,
            end_date=end_date,
            limit_amount=budget.amount,
            spent_amount=0,
            remaining_amount=budget.amount,
            status='active',
        )
        self.db.add(new_cycle)
        self.db.flush()
        return new_cycle

    def close_overlapping_cycles(self, budget_id: int, start_date: date, end_date: date):
        overlapping_cycles = self.db.query(BudgetCycle).filter(
            BudgetCycle.budget_id == budget_id,
            BudgetCycle.status == 'active',
            or_(
                and_(
                    BudgetCycle.start_date <= end_date,
                    BudgetCycle.end_date >= start_date,
                ),
                BudgetCycle.end_date < start_date,
            ),
        ).all()

        for cycle in overlapping_cycles:
            cycle.status = 'closed'
            cycle.closed_at = datetime.now()

    def get_latest_cycle(self, budget_id: int):
        return self.db.query(BudgetCycle).filter(
            BudgetCycle.budget_id == budget_id,
        ).order_by(BudgetCycle.end_date.desc()).first()

    def sync_budget_snapshot(self, budget: Budget, reference_date: date | None = None):
        snapshot_date = reference_date or datetime.now().date()
        cycle = self.get_or_create_cycle(budget, snapshot_date)
        budget.spent_amount = cycle.spent_amount
        budget.remaining_amount = cycle.remaining_amount
        return cycle
