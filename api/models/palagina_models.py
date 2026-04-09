from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, String, DateTime

import os
import sys

if os.getenv("GITHUB_ACTIONS"):
    sys.path.append(os.path.dirname(__file__))
from core.db import Base


class PalaginaState(Base):
    __tablename__ = "palagina_states"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    cookies: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    origins: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
