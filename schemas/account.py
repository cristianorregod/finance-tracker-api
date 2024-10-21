from pydantic import BaseModel, Field
from typing import Optional


class AccountSchema(BaseModel):
    id: Optional[int] = Field(
        None, description="The unique identifier of the account")
    name: str = Field(min_length=3, max_length=25,
                      description="The name of the account")
    initial_balance: float = Field(
        ge=0, description="The initial balance of the account")
    current_balance: float = Field(
        ge=0, description="The current balance of the account")
    account_type: str = Field(min_length=5, max_length=15,
                              description="The type of the account, e.g., bank, cash")

    class Config:
        orm_mode = True
