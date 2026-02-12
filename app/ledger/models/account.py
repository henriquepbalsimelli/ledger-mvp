import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guid: Mapped[uuid.UUID] = mapped_column(String(80), nullable=False, index=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
