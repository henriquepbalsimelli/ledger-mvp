from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Balance(Base):
    __tablename__ = "balance"
    __table_args__ = (
        UniqueConstraint("account_id", "id_asset", name="uq_balance_account_id_asset"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False, index=True)
    id_asset: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False, index=True)

    available: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    locked: Mapped[str] = mapped_column(Numeric(20, 8), nullable=False, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False, onupdate=datetime.now(timezone.utc)
    )

    asset = relationship("Asset", foreign_keys=[id_asset], lazy="subquery")