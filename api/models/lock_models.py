from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, String, DateTime
from api.core.db import Base


class DistributedLock(Base):
    __tablename__ = "distributed_locks"

    lock_name = Column(String, primary_key=True, index=True)
    owner_id = Column(String, nullable=False, index=True)
    acquired_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
