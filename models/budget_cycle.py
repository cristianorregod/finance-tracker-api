from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import relationship
from config.database import Base


class BudgetCycle(Base):
    __tablename__ = 'budget_cycles'
    __table_args__ = (
        UniqueConstraint('budget_id', 'start_date', 'end_date', name='uq_budget_cycles_budget_period'),
    )

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    limit_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, nullable=False, default=0)
    remaining_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default='active')
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    closed_at = Column(DateTime, nullable=True)

    budget = relationship('Budget', back_populates='cycles')
