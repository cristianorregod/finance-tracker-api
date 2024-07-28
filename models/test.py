from sqlalchemy import Column, Integer
from config.database import Base


class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)

    def __repr__(self):
        return f"Test(id={self.id})"
