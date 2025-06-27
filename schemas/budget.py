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
