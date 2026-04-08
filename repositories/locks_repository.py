from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from models.locks_models import DistributedLock


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def acquire_lock(
    db: Session,
    lock_name: str,
    lease_seconds: int = 120,
) -> tuple[bool, str | None]:
    """
    Returns:
        (True, owner_id) if acquired
        (False, None) if already locked and not expired
    """
    owner_id = str(uuid4())
    now = utcnow()
    expires_at = now + timedelta(seconds=lease_seconds)

    existing = (
        db.query(DistributedLock)
        .filter(DistributedLock.lock_name == lock_name)
        .with_for_update()
        .first()
    )

    if existing is None:
        db.add(
            DistributedLock(
                lock_name=lock_name,
                owner_id=owner_id,
                acquired_at=now,
                expires_at=expires_at,
            )
        )
        db.commit()
        return True, owner_id

    if existing.expires_at <= now:
        existing.owner_id = owner_id
        existing.acquired_at = now
        existing.expires_at = expires_at
        db.commit()
        return True, owner_id

    db.rollback()
    return False, None


def release_lock(
    db: Session,
    lock_name: str,
    owner_id: str,
) -> bool:
    """
    Release only if lock belongs to this owner_id.
    """
    existing = (
        db.query(DistributedLock)
        .filter(
            DistributedLock.lock_name == lock_name,
            DistributedLock.owner_id == owner_id,
        )
        .with_for_update()
        .first()
    )

    if existing is None:
        db.rollback()
        return False

    db.delete(existing)
    db.commit()
    return True


def renew_lock(
    db: Session,
    lock_name: str,
    owner_id: str,
    lease_seconds: int = 120,
) -> bool:
    now = utcnow()

    existing = (
        db.query(DistributedLock)
        .filter(
            DistributedLock.lock_name == lock_name,
            DistributedLock.owner_id == owner_id,
        )
        .with_for_update()
        .first()
    )

    if existing is None:
        db.rollback()
        return False

    existing.expires_at = now + timedelta(seconds=lease_seconds)
    db.commit()
    return True


def get_lock_status(
    db: Session,
    lock_name: str,
) -> dict:
    now = utcnow()

    existing = (
        db.query(DistributedLock).filter(DistributedLock.lock_name == lock_name).first()
    )

    if existing is None:
        return {
            "lock_name": lock_name,
            "active": False,
            "owner_id": None,
            "expires_at": None,
        }

    return {
        "lock_name": lock_name,
        "active": existing.expires_at > now,
        "owner_id": existing.owner_id,
        "expires_at": existing.expires_at.isoformat() if existing.expires_at else None,
    }
