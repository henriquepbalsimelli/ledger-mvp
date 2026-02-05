import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String, ForeignKey, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Settlement(Base):
    __tablename__ = "settlement"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False, index=True)
    asset: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    amount: Mapped[str] = mapped_column(Numeric(20, 8), nullable=False)

    from_address: Mapped[str] = mapped_column(String(128), nullable=False)
    to_address: Mapped[str] = mapped_column(String(128), nullable=False)

    tx_hash: Mapped[str] = mapped_column(String(128), nullable=True, index=True)
    id_status: Mapped[int] = mapped_column(ForeignKey("settlement_status.id"), nullable=False, index=True)
    blockchain: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )