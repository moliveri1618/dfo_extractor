import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

RUNNING_IN_AWS = os.getenv("AWS_EXECUTION_ENV") is not None

if not RUNNING_IN_AWS:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
