from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db import Base




class PalaginaState(Base):
    __tablename__ = "palagina_states"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    cookies: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    origins: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
