from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from contextlib import asynccontextmanager
import os
import sys

if os.getenv("GITHUB_ACTIONS"):
    sys.path.append(os.path.dirname(__file__))
from core.db import engine, Base
from routers.v1.palagina_router import router as palagina_router
from routers.v1.lock_router import router as locks_router
from routers.v1.contract import router as contracts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
handler = Mangum(app)


#######################################################################################
#### just for local, in prod lambda invoke the workers directly and remove this #######
#######################################################################################
# import sys

# sys.path.append("/Users/mauro/Documents/plawright_worker")
# from palagina.worker import palagina_nuovo_progetto_worker

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

app.include_router(palagina_router, prefix="/palagina", tags=["Palagina"])
app.include_router(locks_router, prefix="/locks", tags=["Locks"])
app.include_router(contracts_router, prefix="/contracts", tags=["Contracts"])


@app.post("/test-test")
async def test_test():
    return "stocazzooooo"
