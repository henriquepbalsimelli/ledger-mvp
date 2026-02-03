# app/ledger/models.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class LedgerEvent(Base):
    __tablename__ = "ledger_event"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    account_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    asset: Mapped[str] = mapped_column(String(16), nullable=False, index=True)

    # delta representa uma mudança "lógica" (ex: +100 depósito, -100 débito final, etc.)
    delta: Mapped[str] = mapped_column(Numeric(20, 8), nullable=False)

    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    reference_type: Mapped[str] = mapped_column(String(32), nullable=False)
    reference_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)

