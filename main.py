from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from schemas import LoginPayload, NuovoProgettoPayload, EXAMPLE_NUOVO_PROGETTO
from db import engine
from models import Base

app = FastAPI()
Base.metadata.create_all(bind=engine)


#######################################################################################
#### just for local, in prod lambda invoke the workers directly and remove this #######
#######################################################################################
import sys

sys.path.append("/Users/mauro/Documents/plawright_worker")
from palagina_worker import palagina_login_worker, palagina_nuovo_progetto_worker

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
):
    return await palagina_nuovo_progetto_worker(payload=payload, headless=headless)
