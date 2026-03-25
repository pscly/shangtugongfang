from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PromptDraft(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prompt_drafts"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    platform: Mapped[str] = mapped_column(String(32))
    category: Mapped[str] = mapped_column(String(64))
    draft: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
