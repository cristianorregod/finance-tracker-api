from sqlalchemy import Column, Integer
from config.database import Base
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    icon = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="category")
