from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.db.session import engine


@pytest.fixture
def db_session() -> Generator[Session]:
    """Session for the real database, changes are rolled back after each test.

    Used only in tests with ``@pytest.mark.integration``.
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
