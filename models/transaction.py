from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey, Date, Index
from sqlalchemy.orm import relationship
from config.database import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        Index(
            'uq_transactions_recurring_period',
            'recurring_expense_id', 'occurrence_period',
            unique=True,
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "from_account": self.from_account.to_dict() if self.from_account else None,
            "to_account": self.to_account.to_dict() if self.to_account else None,
            "budget": self.budget.to_dict() if self.budget else None,
            "category": self.category.to_dict() if self.category else None,
            "recurring_expense_id": self.recurring_expense_id,
            "occurrence_period": self.occurrence_period,
            "type": self.type,
            "description": self.description,
            "title": self.title,
            "amount": self.amount,
            "transaction_date": self.transaction_date.isoformat(),
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(
        Integer, ForeignKey('accounts.id'), nullable=True, default=None)
    to_account_id = Column(Integer, ForeignKey(
        'accounts.id'), nullable=True, default=None)
    budget_id = Column(Integer, ForeignKey('budgets.id'),
                       nullable=True, default=None)
    type = Column(String, nullable=False)  # 'income' or 'expense' or 'saves'
    category_id = Column(Integer, ForeignKey('categories.id'),
                         nullable=True, default=None)
    description = Column(String, nullable=True)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_date = Column(Date, nullable=False)
    icon = Column(String, nullable=True)
    recurring_expense_id = Column(Integer, ForeignKey('recurring_expenses.id'), nullable=True, index=True)
    occurrence_period = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=False)

    from_account = relationship("Account", foreign_keys=[
                                from_account_id], back_populates="from_transactions")
    to_account = relationship("Account", foreign_keys=[
                              to_account_id], back_populates="to_transactions")
    budget = relationship("Budget", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    recurring_expense = relationship("RecurringExpense", back_populates="transactions")
