import os

from dotenv import load_dotenv

from app.core.config import get_settings

load_dotenv(verbose=True, override=True, dotenv_path=".env.test")

import subprocess
import time

import psycopg
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base

settings = get_settings()


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


POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_CONTAINER_NAME = "test-postgres-container"


def wait_for_postgres():
    for _ in range(30):
        try:
            conn = psycopg.connect(
                host="localhost",
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                dbname=POSTGRES_DB,
            )
            conn.close()
            return
        except Exception:
            time.sleep(1)

    raise RuntimeError("Postgres did not become ready")


def ensure_database_exists():
    conn = psycopg.connect(
        host="localhost",
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        autocommit=True,
    )

    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}'")
        exists = cur.fetchone()

        if not exists:
            cur.execute(f'CREATE DATABASE "{POSTGRES_DB}"')

    conn.close()


@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    print("\n[TEST FIXTURE] Ensuring Postgres container is running")

    # If container is already running, reuse it; otherwise start a new one.
    result = subprocess.run(["docker", "ps", "-q", "-f", f"name={POSTGRES_CONTAINER_NAME}"], capture_output=True)
    if not result.stdout.strip():
        # Clean up any stopped container with the same name
        subprocess.run(["docker", "rm", "-f", POSTGRES_CONTAINER_NAME], check=False, stdout=subprocess.DEVNULL)
        subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-d",
                "--name",
                POSTGRES_CONTAINER_NAME,
                "-e",
                f"POSTGRES_DB={POSTGRES_DB}",
                "-e",
                f"POSTGRES_USER={POSTGRES_USER}",
                "-e",
                f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
                "-p",
                f"{POSTGRES_PORT}:5432",
                "postgres:16",
            ],
            check=True,
        )

    wait_for_postgres()

    yield

    print("\n[TEST FIXTURE] Stopping Postgres container")
    subprocess.run(["docker", "stop", POSTGRES_CONTAINER_NAME], check=False, stdout=subprocess.DEVNULL)


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


@pytest.fixture(scope="function")
def request_mock():
    import uuid

    from starlette.datastructures import Headers
    from starlette.requests import Request

    async def receive():
        return {"type": "http.request", "body": b""}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/test",
        "headers": Headers({"x-request-id": str(uuid.uuid4())}).raw,
        "query_string": b"",
    }

    request = Request(scope, receive)

    request.state.request_id = scope["headers"][0][1].decode()

    return request


@pytest.fixture(scope="session")
def client(postgres_container):
    """
    FastAPI TestClient wired to the test database.
    """
    from fastapi.testclient import TestClient

    import app.main
    from app.core.db import get_db

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(app.main.app) as c:
        yield c


@pytest.fixture()
def freeze_time():
    from freezegun import freeze_time as _freeze

    with _freeze("2024-01-01T00:00:00Z") as frozen:
        yield frozen


def pytest_collection_modifyitems(items):
    """
    Ensure the migration round-trip test runs last to avoid cross-test DB interference
    when the full suite is executed.
    """
    target = None
    for item in list(items):
        if item.nodeid.endswith("test_migrations.py::test_alembic_upgrade_and_downgrade"):
            target = item
            break
    if target:
        items.remove(target)
        items.append(target)


@pytest.fixture(scope="session", autouse=True)
def create_test_schema(postgres_container):
    ensure_database_exists()

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
