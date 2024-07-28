from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import relationship
from config.database import Base


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(
        Integer, ForeignKey('accounts.id'), nullable=True, default=None)
    to_account_id = Column(Integer, ForeignKey(
        'accounts.id'), nullable=True, default=None)
    budget_id = Column(Integer, ForeignKey('budgets.id'),
                       nullable=True, default=None)
    type = Column(String, nullable=False)  # 'income' or 'expense' or 'saves'
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_date = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=False)

    from_account = relationship("Account", foreign_keys=[
                                from_account_id], back_populates="from_transactions")
    to_account = relationship("Account", foreign_keys=[
                              to_account_id], back_populates="to_transactions")
    budget = relationship("Budget", back_populates="transactions")
