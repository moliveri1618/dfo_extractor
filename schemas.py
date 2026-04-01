from pydantic import BaseModel
from typing import List, Optional

class Testata(BaseModel):
    numero: str
    data: str
    addetto: str
    rag_sociale: str
    committente: str
    cf_piva: str
    indirizzo: str
    citta: str
    cap: str
    cellulare: str
    email: str

class Cantiere(BaseModel):
    luogo_zona: str
    tipologia_posa: str
    consegna: str
    tecnico_rilevatore: str
    note_accesso_cantiere: str
    mezzi: str
    persone_necessarie: str

class Contratto(BaseModel):
    fornitore: str
    tipologia: str
    modello: str
    colore: str
    rete: str
    accessori: str
    note: Optional[str] = None

class Rilievo(BaseModel):
    riferimento: str
    larghezza: int
    altezza: int
    tipologia: str
    colore: str
    note: Optional[str] = None

class Zanzariera(BaseModel):
    riferimento: str
    contratto: Contratto
    rilievo: Rilievo

class NuovoProgettoPayload(BaseModel):
    testata: Testata
    cantiere: Cantiere
    zanzariere: List[Zanzariera]


class LoginPayload(BaseModel):
    username: str
    password: str
    remember: bool = False
