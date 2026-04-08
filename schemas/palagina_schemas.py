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




EXAMPLE_NUOVO_PROGETTO = {
    "testata": {
        "numero": "9795",
        "data": "27/11/2025",
        "addetto": "001",
        "rag_sociale": "Tigullio Design SRL",
        "committente": "MADDALONI ANNA",
        "cf_piva": "MDDNNA57C46F924M",
        "indirizzo": "VIA DELLA LIBERTA' 11/6",
        "citta": "GENOVA (GE)",
        "cap": "16129",
        "cellulare": "3282689776",
        "email": "anna.t.maddaloni@gmail.com",
    },
    "cantiere": {
        "luogo_zona": "VIA DOGALI 27/7 - SANTA MARGHERITA LIGURE (GE) - 16038",
        "tipologia_posa": "Rifasciamento telaio esistente",
        "consegna": "60-90 giorni dall'esito definitivo delle misure e dal versamento",
        "tecnico_rilevatore": "Mirko",
        "note_accesso_cantiere": "ci sono 100 metri da fare a piedi",
        "mezzi": "PORTER",
        "persone_necessarie": "2",
    },
    "zanzariere": [
        {
            "riferimento": "B",
            "contratto": {
                "fornitore": "PALAGINA",
                "tipologia": "ZANZARIERA PER FINESTRA",
                "modello": "RV 40 GOLD CRICCHETTO",
                "colore": "RAL 9010",
                "rete": "ANTI BATTERICA",
                "accessori": "DI SERIE",
                "note": "B SALA",
            },
            "rilievo": {
                "riferimento": "B",
                "larghezza": 110,
                "altezza": 152,
                "tipologia": "ZANZARIERA PER FINESTRA",
                "colore": "RAL 9010",
            },
        },
        {
            "riferimento": "G",
            "contratto": {
                "fornitore": "PALAGINA",
                "tipologia": "ZANZARIERA PER FINESTRA",
                "modello": "RV 40 GOLD CRICCHETTO",
                "colore": "RAL 9010",
                "rete": "ANTI BATTERICA",
                "accessori": "DI SERIE",
                "note": "G CUCINA",
            },
            "rilievo": {
                "riferimento": "G",
                "larghezza": 98,
                "altezza": 155,
                "tipologia": "ZANZARIERA PER FINESTRA",
                "colore": "RAL 9010",
                "note": "fare attenzione durante la posa",
            },
        },
    ],
}
