from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class RecurringExpenseCreateSchema(BaseModel):
    account_id: int
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    amount: float = Field(gt=0)
    day_of_month: int = Field(ge=1, le=31)
    start_date: date
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self


class RecurringExpenseUpdateSchema(BaseModel):
    account_id: Optional[int] = None
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class RecurringExpenseSchema(RecurringExpenseCreateSchema):
    id: int
    recurrence: str
    status: str
    last_confirmed_date: Optional[date] = None
    next_occurrence_date: date

    class Config:
        from_attributes = True


class RecurringExpenseConfirmSchema(BaseModel):
    transaction_date: Optional[date] = None
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
