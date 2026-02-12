import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Dominio(Base):
    __tablename__ = "dominio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nm_dominio: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    guid: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, default=lambda: str(uuid.uuid4()))
