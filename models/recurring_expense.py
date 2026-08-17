from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    day_of_month = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    recurrence = Column(String, nullable=False, default="monthly")
    status = Column(String, nullable=False, default="active", index=True)
    last_confirmed_date = Column(Date, nullable=True)
    next_occurrence_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    account = relationship("Account", back_populates="recurring_expenses")
    budget = relationship("Budget", back_populates="recurring_expenses")
    category = relationship("Category", back_populates="recurring_expenses")
    transactions = relationship("Transaction", back_populates="recurring_expense")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
