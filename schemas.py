from datetime import datetime

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    balance: int = 0


class AccountRead(AccountCreate):
    id: int

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    kind: str = Field(pattern="^(income|expense)$")


class CategoryRead(CategoryCreate):
    id: int

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    account_id: int
    category_id: int | None = None
    amount: int = Field(ne=0)
    memo: str | None = Field(default=None, max_length=200)


class TransactionRead(TransactionCreate):
    id: int
    occurred_at: datetime

    model_config = {"from_attributes": True}


class AccountReadWithTransactions(AccountRead):
    transactions: list[TransactionRead] = []


class CategoryStats(BaseModel):
    category: str | None
    total: int
    count: int
