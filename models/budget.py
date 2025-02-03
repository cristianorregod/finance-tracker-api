from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship
from config.database import Base


class Budget(Base):
    __tablename__ = 'budgets'

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, nullable=True, default=0)
    icon = Column(String, nullable=True)
    last_transaction_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=False)

    transactions = relationship("Transaction", back_populates="budget")
