from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from schemas import NuovoProgettoPayload, EXAMPLE_NUOVO_PROGETTO
from db import engine, Base
from dependencies import get_db
from state_service import get_palagina_storage_state, save_palagina_storage_state
from lock_service import acquire_lock, release_lock, renew_lock, get_lock_status
from schemas_lock import ReleaseLockPayload, RenewLockPayload
import json


app = FastAPI()
Base.metadata.create_all(bind=engine)


#######################################################################################
#### just for local, in prod lambda invoke the workers directly and remove this #######
#######################################################################################
import sys

sys.path.append("/Users/mauro/Documents/plawright_worker")
from lambda_handler import handler

#######################################################################################
#######################################################################################
#######################################################################################


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

PALAGINA_CREATE_LOCK_NAME = "palagina_nuovo_progetto_create"
LOCK_LEASE_SECONDS = 120
RELEASE_URL = "http://127.0.0.1:8000/locks/release"

@app.post("/palagina/nuovo-progetto")
async def palagina_nuovo_progetto(
    payload: NuovoProgettoPayload = Body(..., example=EXAMPLE_NUOVO_PROGETTO),
    headless: bool = Query(False),
    db: Session = Depends(get_db),
):
    storage_state = get_palagina_storage_state(db)

    acquired, owner_id = acquire_lock(
        db=db,
        lock_name=PALAGINA_CREATE_LOCK_NAME,
        lease_seconds=LOCK_LEASE_SECONDS,
    )

    if not acquired or not owner_id:
        raise HTTPException(
            status_code=409,
            detail="Another Palagina create-project flow is already in progress.",
        )

    event = {
        "site": "palagina",
        "action": "nuovo_progetto",
        "payload": payload.model_dump(),
        "headless": headless,
        "storage_state": storage_state,
        "lock": {
            "lock_name": PALAGINA_CREATE_LOCK_NAME,
            "owner_id": owner_id,
            "release_url": RELEASE_URL,
        },
    }

    # export event for local lambda testing
    with open("event.json", "w", encoding="utf-8") as f:
        json.dump(event, f, indent=2, ensure_ascii=False, default=str)

    # result = await handler(event, None)

    # updated_storage_state = result.get("updated_storage_state")
    # if updated_storage_state is not None:
    #     save_palagina_storage_state(db, updated_storage_state)

    # return result


@app.post("/locks/release")
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


@app.post("/locks/renew")
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


@app.get("/locks/status")
def lock_status(
    lock_name: str = Query(...),
    db: Session = Depends(get_db),
):
    return get_lock_status(db, lock_name)
