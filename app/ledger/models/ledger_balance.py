import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Balance(Base):
    __tablename__ = "ledger_balance"
    __table_args__ = (UniqueConstraint("account_id", "asset", name="uq_balance_account_asset"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    asset: Mapped[str] = mapped_column(String(16), nullable=False, index=True)

    available: Mapped[str] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    locked: Mapped[str] = mapped_column(Numeric(20, 8), nullable=False, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False, onupdate=datetime.now(timezone.utc)
    )
