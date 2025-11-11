from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.dogs.model import Base
from common.env import get_env

DATABASE_URL = get_env("DATABASE_URL", "postgresql://user:password@db:5432/dogedb")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
