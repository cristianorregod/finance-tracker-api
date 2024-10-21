from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class TransactionSchema(BaseModel):
    id: Optional[int] = Field(
        None, description="The unique identifier of the transaction")
    from_account_id: Optional[int] = Field(None,
                                           description="Reference to account from money was spent")
    to_account_id: Optional[int] = Field(None,
                                         description="Reference to account to money was received")
    budget_id: Optional[int] = Field(None,
                                     description="Reference to budget for the transaction")
    type: str = Field(min_length=3, max_length=25,
                      description="Describe the transaction type")
    description: str = Field(min_length=10, max_length=50,
                             description="Short description or name of the transaction")
    amount: float = Field(
        ge=0, description="The expense for the current transaction")
    transaction_date: date = Field(
        description="The date when transaction is applied")

    class Config:
        orm_mode = True
