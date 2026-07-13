# database.py

from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ----------------------------
# User
# ----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    wallet = relationship(
        "Wallet",
        back_populates="user",
        uselist=False
    )


# ----------------------------
# Wallet
# ----------------------------
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    balance = Column(
        Float,
        default=0.0
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="wallet"
    )


# ----------------------------
# Transaction
# ----------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    amount = Column(Float)

    transaction_type = Column(
        String(20)
    )  # CREDIT / DEBIT

    description = Column(
        String(255)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ----------------------------
# Reward
# ----------------------------
class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    reward_name = Column(
        String(100)
    )

    reward_amount = Column(Float)

    claimed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ----------------------------
# Create Tables
# ----------------------------
def create_tables():
    Base.metadata.create_all(bind=engine)


# ----------------------------
# DB Dependency
# ----------------------------
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
