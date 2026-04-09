from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from api.routers.dependencies import get_db
from api.schemas.palagina_schemas import NuovoProgettoPayload, EXAMPLE_NUOVO_PROGETTO
from api.services.palagina_service import run_nuovo_progetto

router = APIRouter()


# @router.post("/nuovo-progetto")
# async def palagina_nuovo_progetto(
#     payload: NuovoProgettoPayload = Body(..., example=EXAMPLE_NUOVO_PROGETTO),
#     headless: bool = Query(False),
#     db: Session = Depends(get_db),
# ):
#     return await run_nuovo_progetto(db=db, payload=payload, headless=headless)


@router.post("/test-test")
async def test_test(
):
    return 'stocazzooooo'
