import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

load_dotenv(verbose=True, override=True, dotenv_path=".env.test")

settings = get_settings()
from app.core.db import Base

# Engine exclusiva para testes
engine = create_engine(
    settings.database_url,
    echo=False,
    future=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session", autouse=True)
def create_test_schema():
    """
    Cria todas as tabelas antes da suíte de testes
    e remove ao final.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Cada teste roda dentro de uma transação isolada.
    Tudo é revertido ao final do teste.
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()