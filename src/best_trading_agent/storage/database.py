from collections.abc import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

SessionFactory = Callable[[], Session]


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(database_url, future=True)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)
