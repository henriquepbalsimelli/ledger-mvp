import uuid

from sqlalchemy import String, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SettlementStatus(Base):
    __tablename__ = "settlement_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    settlement_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
