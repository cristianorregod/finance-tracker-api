import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.database import Base
from models.account import Account
from models.recurring_expense import RecurringExpense
from schemas.recurring_expense import (
    RecurringExpenseConfirmSchema,
    RecurringExpenseCreateSchema,
)
from services.recurring_expense import RecurringExpenseService


class RecurringExpenseServiceTests(unittest.TestCase):
    def setUp(self):
        import models.budget, models.category, models.transaction

        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(Account(name="Checking", initial_balance=1000, current_balance=1000, account_type="cash"))
        self.db.commit()
        self.service = RecurringExpenseService(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_month_end_occurrences_are_clamped(self):
        expense = self.service.create(RecurringExpenseCreateSchema(
            account_id=1, name="Monthly rent", amount=100, day_of_month=31,
            start_date=date(2025, 1, 31),
        ))
        self.service.confirm(expense.id, RecurringExpenseConfirmSchema(transaction_date=date(2025, 1, 31)))
        self.db.refresh(expense)
        self.assertEqual(expense.next_occurrence_date, date(2025, 2, 28))

    def test_first_occurrence_is_not_before_start_date(self):
        expense = self.service.create(RecurringExpenseCreateSchema(
            account_id=1, name="Monthly rent", amount=100, day_of_month=1,
            start_date=date(2025, 1, 15),
        ))
        self.assertEqual(expense.next_occurrence_date, date(2025, 2, 1))

    def test_confirmation_uses_override_date_for_transaction(self):
        expense = self.service.create(RecurringExpenseCreateSchema(
            account_id=1, name="Monthly rent", amount=100, day_of_month=15,
            start_date=date(2025, 1, 15),
        ))
        transaction, _ = self.service.confirm(
            expense.id,
            RecurringExpenseConfirmSchema(transaction_date=date(2025, 1, 20)),
        )
        self.assertEqual(transaction.transaction_date, date(2025, 1, 20))

    def test_confirmation_is_idempotent_for_same_period(self):
        expense = self.service.create(RecurringExpenseCreateSchema(
            account_id=1, name="Monthly rent", amount=100, day_of_month=15,
            start_date=date(2025, 1, 15),
        ))
        self.service.confirm(expense.id, RecurringExpenseConfirmSchema(transaction_date=date(2025, 1, 15)))
        expense.next_occurrence_date = date(2025, 1, 15)
        self.db.commit()
        with self.assertRaisesRegex(ValueError, "already confirmed"):
            self.service.confirm(expense.id, RecurringExpenseConfirmSchema(transaction_date=date(2025, 1, 15)))

    def test_financial_failure_rolls_back_transaction_and_schedule(self):
        account = self.db.query(Account).one()
        account.current_balance = 50
        self.db.commit()
        expense = self.service.create(RecurringExpenseCreateSchema(
            account_id=account.id, name="Monthly rent", amount=100, day_of_month=31,
            start_date=date(2025, 1, 31),
        ))
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            self.service.confirm(expense.id, RecurringExpenseConfirmSchema(transaction_date=date(2025, 1, 31)))
        self.db.refresh(expense)
        self.assertEqual(account.current_balance, 50)
        self.assertIsNone(expense.last_confirmed_date)
        self.assertEqual(self.db.query(RecurringExpense).count(), 1)


if __name__ == "__main__":
    unittest.main()
