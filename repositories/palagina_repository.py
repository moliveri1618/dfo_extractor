from sqlalchemy.orm import Session
from models.palagina_models import PalaginaState

PALAGINA_STATE_NAME = "palagina"


def get_palagina_storage_state(db: Session) -> dict | None:
    row = (
        db.query(PalaginaState)
        .filter(PalaginaState.name == PALAGINA_STATE_NAME)
        .first()
    )

    if not row:
        return None

    return {
        "cookies": row.cookies or [],
        "origins": row.origins or [],
    }


def save_palagina_storage_state(db: Session, storage_state: dict) -> None:
    row = (
        db.query(PalaginaState)
        .filter(PalaginaState.name == PALAGINA_STATE_NAME)
        .first()
    )

    cookies = storage_state.get("cookies", [])
    origins = storage_state.get("origins", [])

    if row:
        row.cookies = cookies
        row.origins = origins
    else:
        row = PalaginaState(
            name=PALAGINA_STATE_NAME,
            cookies=cookies,
            origins=origins,
        )
        db.add(row)

    db.commit()
