from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import sys

# from sqlalchemy.orm import Session
# from schemas.palagina_schemas import NuovoProgettoPayload, EXAMPLE_NUOVO_PROGETTO

if os.getenv("GITHUB_ACTIONS"):
    sys.path.append(os.path.dirname(__file__))
# from routers.dependencies import get_db
# from repositories.palagina_repository import get_palagina_storage_state, save_palagina_storage_state
# from repositories.lock_repository import acquire_lock, release_lock, renew_lock, get_lock_status
# from schemas.lock_schema import ReleaseLockPayload, RenewLockPayload
# import json
# from core.db import engine, Base
# from routers.v1.palagina_router import router as palagina_router
# from routers.v1.lock_router import router as locks_router


app = FastAPI()
handler = Mangum(app=app)
# Base.metadata.create_all(bind=engine)


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

# app.include_router(palagina_router, prefix="/palagina", tags=["Palagina"])
# app.include_router(locks_router, prefix="/locks", tags=["Locks"])


@app.post("/test-test")
async def test_test():
    return "stocazzooooo"


# @app.post("/locks/release")
# def release_lock_endpoint(
#     payload: ReleaseLockPayload,
#     db: Session = Depends(get_db),
# ):
#     ok = release_lock(
#         db=db,
#         lock_name=payload.lock_name,
#         owner_id=payload.owner_id,
#     )

#     if not ok:
#         raise HTTPException(
#             status_code=404,
#             detail="Lock not found, expired, or owner_id mismatch.",
#         )

#     return {"success": True}


# @app.post("/locks/renew")
# def renew_lock_endpoint(
#     payload: RenewLockPayload,
#     db: Session = Depends(get_db),
# ):
#     ok = renew_lock(
#         db=db,
#         lock_name=payload.lock_name,
#         owner_id=payload.owner_id,
#         lease_seconds=payload.lease_seconds,
#     )

#     if not ok:
#         raise HTTPException(
#             status_code=404,
#             detail="Lock not found, expired, or owner_id mismatch.",
#         )

#     return {"success": True}


# @app.get("/locks/status")
# def lock_status(
#     lock_name: str = Query(...),
#     db: Session = Depends(get_db),
# ):
#     return get_lock_status(db, lock_name)
