import uuid

from dotenv import load_dotenv

from app.core.config import get_settings
import os
load_dotenv(verbose=True, override=True, dotenv_path=".env.test")

import subprocess
import time
import pytest
import psycopg
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


POSTGRES_PORT=os.getenv("POSTGRES_PORT")
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB=os.getenv("POSTGRES_DB")
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
        dbname="postgres",  # database default
        autocommit=True,
    )

    with conn.cursor() as cur:
        cur.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}'"
        )
        exists = cur.fetchone()

        if not exists:
            cur.execute(f'CREATE DATABASE "{POSTGRES_DB}"')

    conn.close()

@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    print("\n[TEST FIXTURE] Starting Postgres container")

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
    subprocess.run(
        ["docker", "stop", POSTGRES_CONTAINER_NAME],
        check=False,
    )


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
    from starlette.requests import Request
    from starlette.datastructures import Headers
    import uuid

    async def receive():
        return {"type": "http.request", "body": b""}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/test",
        "headers": Headers({
            "x-request-id": str(uuid.uuid4())
        }).raw,
        "query_string": b"",
    }

    request = Request(scope, receive)

    # 🔑 ESSENCIAL: simula middleware
    request.state.request_id = scope["headers"][0][1].decode()

    return request

@pytest.fixture(scope="session", autouse=True)
def create_test_schema(postgres_container):

    # garante que o database existe
    ensure_database_exists()


    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)