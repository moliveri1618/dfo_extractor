from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from routers.dependencies import get_db
from schemas.locks_schema import ReleaseLockPayload, RenewLockPayload
from repositories.locks_repository import release_lock, renew_lock, get_lock_status

router = APIRouter()


@router.post("/release")
def release_lock_endpoint(
    payload: ReleaseLockPayload,
    db: Session = Depends(get_db),
):
    ok = release_lock(
        db=db,
        lock_name=payload.lock_name,
        owner_id=payload.owner_id,
    )

    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Lock not found, expired, or owner_id mismatch.",
        )

    return {"success": True}


@router.post("/renew")
def renew_lock_endpoint(
    payload: RenewLockPayload,
    db: Session = Depends(get_db),
):
    ok = renew_lock(
        db=db,
        lock_name=payload.lock_name,
        owner_id=payload.owner_id,
        lease_seconds=payload.lease_seconds,
    )

    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Lock not found, expired, or owner_id mismatch.",
        )

    return {"success": True}


@router.get("/status")
def lock_status(
    lock_name: str = Query(...),
    db: Session = Depends(get_db),
):
    return get_lock_status(db, lock_name)
