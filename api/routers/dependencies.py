import os
import sys
if os.getenv("GITHUB_ACTIONS"):
    sys.path.append(os.path.dirname(__file__))

from core.db import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
