# wallet.py

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import (
    Wallet,
    Transaction,
    get_db
)

from auth import get_current_user
from schemas import WalletResponse
from database import User

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)


# ------------------------------------
# Get Wallet Details
# ------------------------------------
@router.get(
    "/me",
    response_model=WalletResponse
)
def get_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found."
        )

    return wallet


# ------------------------------------
# Get Wallet Balance
# ------------------------------------
@router.get("/balance")
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found."
        )

    return {
        "user_id": current_user.id,
        "balance": wallet.balance,
        "last_updated": wallet.updated_at
    }


# ------------------------------------
# Add Money (Demo)
# ------------------------------------
@router.post("/add-money")
def add_money(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0."
        )

    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found."
        )

    wallet.balance += amount

    transaction = Transaction(
        user_id=current_user.id,
        amount=amount,
        transaction_type="CREDIT",
        description="Money Added",
        created_at=datetime.utcnow()
    )

    db.add(transaction)
    db.commit()
    db.refresh(wallet)

    return {
        "message": "Money added successfully.",
        "balance": wallet.balance
    }


# ------------------------------------
# Spend Money
# ------------------------------------
@router.post("/spend-money")
def spend_money(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0."
        )

    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .first()
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found."
        )

    if wallet.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance."
        )

    wallet.balance -= amount

    transaction = Transaction(
        user_id=current_user.id,
        amount=amount,
        transaction_type="DEBIT",
        description="Money Spent",
        created_at=datetime.utcnow()
    )

    db.add(transaction)
    db.commit()
    db.refresh(wallet)

    return {
        "message": "Payment successful.",
        "balance": wallet.balance
    }


# ------------------------------------
# Transaction History
# ------------------------------------
from typing import List
from schemas import TransactionResponse


@router.get(
    "/transactions",
    response_model=List[TransactionResponse]
)
def get_transaction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return transactions


# ------------------------------------
# Recent Transactions
# ------------------------------------
@router.get("/transactions/recent")
def get_recent_transactions(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100."
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "count": len(transactions),
        "transactions": transactions
    }


# ------------------------------------
# Transaction By ID
# ------------------------------------
@router.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found."
        )

    return transaction
