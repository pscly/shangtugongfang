from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    platform: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    credits_estimated: Mapped[int] = mapped_column(Integer, default=0)
    credits_frozen: Mapped[int] = mapped_column(Integer, default=0)
    credits_captured: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))


class JobItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_items"

    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    category: Mapped[str] = mapped_column(String(64))
    prompt_draft_id: Mapped[str | None] = mapped_column(ForeignKey("prompt_drafts.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    provider_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    pricing_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    credits_estimated: Mapped[int] = mapped_column(Integer, default=0)
    credits_captured: Mapped[int] = mapped_column(Integer, default=0)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
