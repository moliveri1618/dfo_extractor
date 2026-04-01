from fastapi import FastAPI, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from schemas import NuovoProgettoPayload, EXAMPLE_NUOVO_PROGETTO
from db import engine, Base
from dependencies import get_db
from state_service import get_palagina_storage_state, save_palagina_storage_state

app = FastAPI()
Base.metadata.create_all(bind=engine)


#######################################################################################
#### just for local, in prod lambda invoke the workers directly and remove this #######
#######################################################################################
import sys

sys.path.append("/Users/mauro/Documents/plawright_worker")
from palagina_worker import palagina_nuovo_progetto_worker

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


@app.post("/palagina/nuovo-progetto")
async def palagina_nuovo_progetto(
    payload: NuovoProgettoPayload = Body(..., example=EXAMPLE_NUOVO_PROGETTO),
    headless: bool = Query(False),
    db: Session = Depends(get_db),
):
    storage_state = get_palagina_storage_state(db)

    result = await palagina_nuovo_progetto_worker(
        payload=payload,
        headless=headless,
        storage_state=storage_state,
    )

    updated_storage_state = result.get("updated_storage_state")
    if updated_storage_state is not None:
        save_palagina_storage_state(db, updated_storage_state)

    return result
