# schemas.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# -----------------------------
# Authentication
# -----------------------------
class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------
# User Response
# -----------------------------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


# -----------------------------
# Wallet
# -----------------------------
class WalletResponse(BaseModel):
    balance: float

    class Config:
        from_attributes = True


class WalletUpdate(BaseModel):
    amount: float = Field(..., gt=0)


# -----------------------------
# Transaction
# -----------------------------
class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: str


class TransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# Reward
# -----------------------------
class RewardResponse(BaseModel):
    id: int
    reward_name: str
    reward_amount: float
    claimed: bool

    class Config:
        from_attributes = True


# -----------------------------
# Message
# -----------------------------
class Message(BaseModel):
    message: str
