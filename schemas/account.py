from pydantic import BaseModel, Field
from typing import Optional


class AccountSchema(BaseModel):
    id: Optional[int] = Field(
        None, description="The unique identifier of the account")
    name: str = Field(min_length=3, max_length=25,
                      description="The name of the account")
    balance: float = Field(ge=0, description="The balance of the account")
    this_month_expense: Optional[float] = Field(None, ge=0,
                                                description="The expense for the current month")
    this_month_income: Optional[float] = Field(None, ge=0,
                                               description="The income for the current month")
    account_type: str = Field(min_length=5, max_length=15,
                              description="The type of the account, e.g., bank, cash")

    class Config:
        orm_mode = True
