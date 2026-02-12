from app.ledger.models import Dominio


class DominioRepository:
    def __init__(self, db):
        self.db = db

    def get_status_by_id(self, status_id: int):
        return self.db.query(Dominio).filter(Dominio.id == status_id).first()

    def get_status_by_name(self, status: str):
        return self.db.query(Dominio).filter(Dominio.nm_dominio == status).first()
