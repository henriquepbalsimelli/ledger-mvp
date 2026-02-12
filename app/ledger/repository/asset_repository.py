from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ledger.models import Asset


class AssetRepository:
    """Simple repository to resolve asset names to IDs and create if missing."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, nm_asset: str) -> Asset | None:
        return self.db.execute(select(Asset).where(Asset.nm_asset == nm_asset)).scalar_one_or_none()

    def get_or_create(self, nm_asset: str) -> Asset:
        asset = self.get_by_name(nm_asset)
        if asset:
            return asset
        asset = Asset(nm_asset=nm_asset)
        self.db.add(asset)
        self.db.flush()
        return asset
