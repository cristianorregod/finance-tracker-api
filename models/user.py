from config.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=False)

