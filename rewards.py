# rewards.py

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import (
    Reward,
    Wallet,
    Transaction,
    User,
    get_db,
)

router = APIRouter(
    prefix="/rewards",
    tags=["Rewards"]
)

DAILY_REWARD_AMOUNT = 20


# ----------------------------------------
# Claim Daily Reward
# ----------------------------------------
@router.post("/daily")
def claim_daily_reward(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    last_reward = (
        db.query(Reward)
        .filter(
            Reward.user_id == current_user.id,
            Reward.reward_name == "Daily Reward"
        )
        .order_by(Reward.created_at.desc())
        .first()
    )

    if last_reward:
        next_time = last_reward.created_at + timedelta(days=1)

        if datetime.utcnow() < next_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Daily reward already claimed."
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

    wallet.balance += DAILY_REWARD_AMOUNT

    reward = Reward(
        user_id=current_user.id,
        reward_name="Daily Reward",
        reward_amount=DAILY_REWARD_AMOUNT,
        claimed=True,
        created_at=datetime.utcnow()
    )

    transaction = Transaction(
        user_id=current_user.id,
        amount=DAILY_REWARD_AMOUNT,
        transaction_type="CREDIT",
        description="Daily Reward",
        created_at=datetime.utcnow()
    )

    db.add(reward)
    db.add(transaction)

    db.commit()
    db.refresh(wallet)

    return {
        "message": "Daily reward claimed successfully.",
        "reward": DAILY_REWARD_AMOUNT,
        "balance": wallet.balance
    }


from typing import List
from schemas import RewardResponse


# ----------------------------------------
# Reward History
# ----------------------------------------
@router.get(
    "/history",
    response_model=List[RewardResponse]
)
def reward_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    rewards = (
        db.query(Reward)
        .filter(Reward.user_id == current_user.id)
        .order_by(Reward.created_at.desc())
        .all()
    )

    return rewards


# ----------------------------------------
# Reward Details
# ----------------------------------------
@router.get("/{reward_id}")
def reward_details(
    reward_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    reward = (
        db.query(Reward)
        .filter(
            Reward.id == reward_id,
            Reward.user_id == current_user.id
        )
        .first()
    )

    if reward is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found."
        )

    return reward


# ----------------------------------------
# Reward Claim Status
# ----------------------------------------
@router.get("/status/today")
def reward_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    reward = (
        db.query(Reward)
        .filter(
            Reward.user_id == current_user.id,
            Reward.reward_name == "Daily Reward"
        )
        .order_by(Reward.created_at.desc())
        .first()
    )

    if reward is None:
        return {
            "claimed": False,
            "reward": 20
        }

    next_claim = reward.created_at + timedelta(days=1)

    return {
        "claimed": datetime.utcnow() < next_claim,
        "last_claim": reward.created_at,
        "next_claim": next_claim
    }


# ----------------------------------------
# Available Rewards
# ----------------------------------------
@router.get("/available")
def available_rewards(
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

    last_reward = (
        db.query(Reward)
        .filter(
            Reward.user_id == current_user.id,
            Reward.reward_name == "Daily Reward"
        )
        .order_by(Reward.created_at.desc())
        .first()
    )

    can_claim = True
    next_claim = None

    if last_reward:
        next_claim = last_reward.created_at + timedelta(days=1)
        if datetime.utcnow() < next_claim:
            can_claim = False

    return {
        "daily_reward": DAILY_REWARD_AMOUNT,
        "can_claim": can_claim,
        "next_claim": next_claim,
        "current_balance": wallet.balance
    }


# ----------------------------------------
# Reward Statistics
# ----------------------------------------
@router.get("/stats")
def reward_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rewards = (
        db.query(Reward)
        .filter(Reward.user_id == current_user.id)
        .all()
    )

    total_rewards = len(rewards)
    total_amount = sum(r.reward_amount for r in rewards)

    return {
        "total_rewards": total_rewards,
        "total_reward_amount": total_amount
    }
