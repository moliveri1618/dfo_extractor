from sqlalchemy.orm import Session
from fastapi import HTTPException
import boto3
import json

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
    print("storage_state loaded:")
    print(storage_state)

    lambda_client = boto3.client("lambda", region_name="eu-north-1")
    print(lambda_client)

    acquired, owner_id = acquire_lock(
        db=db,
        lock_name=PALAGINA_CREATE_LOCK_NAME,
        lease_seconds=LOCK_LEASE_SECONDS,
    )
    print("lock acquisition result:")
    print(f"acquired = {acquired}")
    print(f"owner_id = {owner_id}")

    if not acquired or not owner_id:
        raise HTTPException(
            status_code=409,
            detail="Another Palagina create-project flow is already in progress.",
        )

    print("payload received:")
    print(payload)
    print("headless:")
    print(headless)
    print("lock_name:")
    print(PALAGINA_CREATE_LOCK_NAME)
    print("release_url:")
    print(RELEASE_URL)

    event = {
        "site": "palagina",
        "action": "nuovo_progetto",
        "payload": payload.model_dump(mode="json"),
        "headless": headless,
        "storage_state": storage_state,
        "lock": {
            "lock_name": PALAGINA_CREATE_LOCK_NAME,
            "owner_id": owner_id,  # later from acquire_lock
            "release_url": RELEASE_URL,
        },
    }

    response = lambda_client.invoke(
        FunctionName="playwright_worker",  
        InvocationType="RequestResponse",
        Payload=json.dumps(event).encode("utf-8"),
    )

    print("lambda response raw:", response)

    raw_payload = response["Payload"].read()
    print("lambda payload raw:", raw_payload)

    result = json.loads(raw_payload)
    print("lambda result parsed:", result)

    updated_storage_state = result.get("updated_storage_state")
    if updated_storage_state is not None:
        save_palagina_storage_state(db, updated_storage_state)
        print("storage_state saved successfully")

    return result

