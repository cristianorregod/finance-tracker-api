from config.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship


class Account(Base):
    __tablename__ = 'accounts'

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    initial_balance = Column(Float, nullable=False,  default=0)
    current_balance = Column(Float, nullable=True, default=0)
    account_type = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    last_transaction_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=False)

    from_transactions = relationship(
        "Transaction", foreign_keys='Transaction.from_account_id', back_populates="from_account")
    to_transactions = relationship(
        "Transaction", foreign_keys='Transaction.to_account_id', back_populates="to_account")
