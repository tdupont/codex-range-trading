from sqlalchemy.orm import Session

from app.db.session import get_db_session


def get_db() -> Session:
    yield from get_db_session()
