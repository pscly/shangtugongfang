from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class CreditWallet(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "credit_wallets"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), unique=True, index=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    frozen_balance: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CreditLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "credit_ledgers"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_credit_idempotency"),)

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(32))
    amount: Mapped[int] = mapped_column(Integer)
    related_entity_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    related_entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RechargeCardBatch(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recharge_card_batches"

    name: Mapped[str] = mapped_column(String(128))
    credits_amount: Mapped[int] = mapped_column(Integer)
    total_count: Mapped[int] = mapped_column(Integer)
    issued_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RechargeCard(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recharge_cards"

    batch_id: Mapped[str] = mapped_column(ForeignKey("recharge_card_batches.id"), index=True)
    card_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    credits_amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="unused")
    issued_to_workspace_id: Mapped[str | None] = mapped_column(ForeignKey("workspaces.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RechargeRedemption(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recharge_redemptions"
    __table_args__ = (UniqueConstraint("recharge_card_id", name="uq_recharge_card_redeem"),)

    recharge_card_id: Mapped[str] = mapped_column(ForeignKey("recharge_cards.id"))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"))
    redeemed_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
