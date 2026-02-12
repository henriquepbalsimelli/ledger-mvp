from datetime import datetime, timezone

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Asset(Base):
    """Asset catalog used to normalize asset references across tables."""

    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("nm_asset", name="uq_asset"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nm_asset: Mapped[str] = mapped_column(String(16), nullable=False, index=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
        onupdate=datetime.now(timezone.utc),
    )
