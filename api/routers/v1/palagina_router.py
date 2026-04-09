from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

import os
import sys
if os.getenv("GITHUB_ACTIONS"):
    sys.path.append(os.path.dirname(__file__))

from routers.dependencies import get_db
from schemas.palagina_schemas import NuovoProgettoPayload, EXAMPLE_NUOVO_PROGETTO
from services.palagina_service import run_nuovo_progetto

router = APIRouter()


@router.post("/nuovo-progetto")
async def palagina_nuovo_progetto(
    payload: NuovoProgettoPayload = Body(..., example=EXAMPLE_NUOVO_PROGETTO),
    headless: bool = Query(True),
    db: Session = Depends(get_db),
):
    return await run_nuovo_progetto(db=db, payload=payload, headless=headless)


@router.post("/test-test-Y000")
async def test_testYOOO(
):
    return 'stocazzooooo'
