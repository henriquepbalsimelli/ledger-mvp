import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import BIGINT, DateTime, ForeignKey, Numeric, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class BalanceHold(Base):
    __tablename__ = "balance_hold"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False, index=True)
    id_asset: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False, index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)

    reason: Mapped[str] = mapped_column(String(128))
    # LOCK | SETTLEMENT

    reference_id: Mapped[str] = mapped_column(String(128))
    # ex: order_id, settlement_id

    id_status: Mapped[int] = mapped_column(ForeignKey("dominio.id"), nullable=False, index=True)
    # ACTIVE | RELEASED | CONSUMED

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    asset = relationship("Asset", foreign_keys=[id_asset], lazy="subquery")

    status = relationship("Dominio", foreign_keys=[id_status], lazy="subquery")
