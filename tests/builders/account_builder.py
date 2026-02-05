import uuid

from app.ledger.models.account import Account


class AccountBuilder:
    def __init__(self, db_session, guid=uuid.uuid4()):
        self.db_session = db_session
        self._account = {
            "guid": guid,
        }

    class Meta:
        model = Account

    def build(self, **overrides):
        instance = self.Meta.model(**self._account)
        self.db_session.add(instance)
        self.db_session.commit()
        return instance
