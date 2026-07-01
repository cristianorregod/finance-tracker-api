from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class BudgetSchema(BaseModel):
    id: Optional[int] = Field(
        None, description="The unique identifier of the budget")
    name: str = Field(min_length=3, max_length=25,
                      description="The name of the budget")
    description: Optional[str] = Field(None,
                                       description="The description of the budget")
    amount: float = Field(ge=0, description="The amount of the budget")
    period_type: Optional[str] = Field(
        default="monthly", description="Budget period type")
    remaining_amount: float = Field(
        description="The remaining amount of the budget")
    spent_amount: Optional[float] = Field(None,
                                          description="The remaining amount of the budget")
    icon: Optional[str] = Field(
        None, description="The icon of the budget")
    last_transaction_date: Optional[date] = Field(
        None, description="The last transaction date of the budget")

    class Config:
        from_attributes = True


class BudgetUpdateSchema(BaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=25, description="The name of the budget")
    description: Optional[str] = Field(
        None, description="The description of the budget")
    amount: Optional[float] = Field(
        None, ge=0, description="The amount of the budget")
    period_type: Optional[str] = Field(
        None, description="Budget period type")
    icon: Optional[str] = Field(
        None, description="The icon of the budget")


class BudgetCycleSummarySchema(BaseModel):
    id: int
    budget_id: int
    start_date: date
    end_date: date
    limit_amount: float
    spent_amount: float
    remaining_amount: float
    status: str

    class Config:
        from_attributes = True


class BudgetReadSchema(BudgetSchema):
    active_cycle: Optional[BudgetCycleSummarySchema] = Field(
        None, description="Current budget cycle")
