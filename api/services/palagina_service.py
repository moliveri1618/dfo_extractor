from sqlalchemy.orm import Session
from fastapi import HTTPException

import os
import sys
if os.getenv("GITHUB_ACTIONS"):
    sys.path.append(os.path.dirname(__file__))

from schemas.palagina_schemas import NuovoProgettoPayload
from repositories.palagina_repository import (
    get_palagina_storage_state, 
    save_palagina_storage_state
)
from repositories.lock_repository import acquire_lock
from core.config import (
    PALAGINA_CREATE_LOCK_NAME,
    RELEASE_URL,
    LOCK_LEASE_SECONDS,
)

#######################################################################################
#### just for local, in prod lambda invoke the workers directly and remove this #######
#######################################################################################
# import sys

# sys.path.append("/Users/mauro/Documents/plawright_worker")
# from palagina.worker import palagina_nuovo_progetto_worker

#######################################################################################
#######################################################################################
#######################################################################################

async def run_nuovo_progetto(
    db: Session, payload: NuovoProgettoPayload, headless: bool
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

    # result = await palagina_nuovo_progetto_worker(
    #     payload=payload,
    #     headless=headless,
    #     storage_state=storage_state,
    #     lock_name=PALAGINA_CREATE_LOCK_NAME,
    #     owner_id=owner_id,
    #     release_url=RELEASE_URL,
    # )

    # updated_storage_state = result.get("updated_storage_state")
    # if updated_storage_state is not None:
    #     save_palagina_storage_state(db, updated_storage_state)

    # return result
    return 1


# PALAGINA_CREATE_LOCK_NAME = "palagina_nuovo_progetto_create"
# LOCK_LEASE_SECONDS = 120
# RELEASE_URL = "http://127.0.0.1:8000/locks/release"

# @app.post("/palagina/nuovo-progetto")
# async def palagina_nuovo_progetto(
#     payload: NuovoProgettoPayload = Body(..., example=EXAMPLE_NUOVO_PROGETTO),
#     headless: bool = Query(False),
#     db: Session = Depends(get_db),
# ):

#     return await run_nuovo_progetto(db=db, payload=payload, headless=headless)
#     # storage_state = get_palagina_storage_state(db)

#     # # acquired, owner_id = acquire_lock(
#     # #     db=db,
#     # #     lock_name=PALAGINA_CREATE_LOCK_NAME,
#     # #     lease_seconds=LOCK_LEASE_SECONDS,
#     # # )

#     # # if not acquired or not owner_id:
#     # #     raise HTTPException(
#     # #         status_code=409,
#     # #         detail="Another Palagina create-project flow is already in progress.",
#     # #     )

#     # # event = {
#     # #     "site": "palagina",
#     # #     "action": "nuovo_progetto",
#     # #     "payload": payload.model_dump(),
#     # #     "headless": headless,
#     # #     "storage_state": storage_state,
#     # #     "lock": {
#     # #         "lock_name": PALAGINA_CREATE_LOCK_NAME,
#     # #         "owner_id": owner_id,
#     # #         "release_url": RELEASE_URL,
#     # #     },
#     # # }

#     # # # export event for local lambda testing
#     # # with open("event.json", "w", encoding="utf-8") as f:
#     # #     json.dump(event, f, indent=2, ensure_ascii=False, default=str)

#     # result = await palagina_nuovo_progetto_worker(
#     #     payload=payload,
#     #     headless=headless,
#     #     storage_state=storage_state,
#     #     lock_name=PALAGINA_CREATE_LOCK_NAME,
#     #     # owner_id=owner_id,
#     #     release_url=RELEASE_URL,
#     # )

#     # updated_storage_state = result.get("updated_storage_state")
#     # if updated_storage_state is not None:
#     #     save_palagina_storage_state(db, updated_storage_state)

#     # return result
