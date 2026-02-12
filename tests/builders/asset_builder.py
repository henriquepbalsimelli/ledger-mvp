from app.ledger.models.assets import Asset


class AssetBuilder:
    def __init__(self, db_session, nm_asset: str = "USDC"):
        self.db_session = db_session
        self._asset = {"nm_asset": nm_asset}
        self.nm_asset = nm_asset

    class Meta:
        model = Asset

    def build(self, **overrides):
        data = {**self._asset, **overrides}
        instance = self.Meta.model(**data)
        self.db_session.add(instance)
        self.db_session.commit()
        return instance

    def get_or_create(self):
        instance = self.db_session.query(self.Meta.model).filter_by(nm_asset=self.nm_asset).first()
        if instance:
            return instance
        return self.build(nm_asset=self.nm_asset)
