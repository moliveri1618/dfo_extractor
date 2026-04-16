# 🚀 dfo_extractor

Playwright-based web scraper for DFO extraction with FastAPI integration.

---

## 📦 Setup

### 1. Create virtual environment

Inside your project folder:

```bash
python3 -m venv venv
```

### 2. Activate the environment


```bash
source venv/bin/activate
```


### 3. Install dependencies


```bash
python -m pip install -r requirements.txt
```


### 4. Run the api


```bash
uvicorn main:app --reload
```







{
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
    "email": "anna.t.maddaloni@gmail.com"
  },
  "cantiere": {
    "luogo_zona": "VIA DOGALI 27/7 - SANTA MARGHERITA LIGURE (GE) - 16038",
    "tipologia_posa": "Rifasciamento telaio esistente",
    "consegna": "60-90 giorni dall'esito definitivo delle misure e dal versamento",
    "tecnico_rilevatore": "Mirko",
    "note_accesso_cantiere": "ci sono 100 metri da fare a piedi",
    "mezzi": "PORTER",
    "persone_necessarie": "2"
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
        "note": "B SALA"
      },
      "rilievo": {
        "riferimento": "B",
        "larghezza": 110,
        "altezza": 152,
        "tipologia": "ZANZARIERA PER FINESTRA",
        "colore": "RAL 9010"
      }
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
        "note": "G CUCINA"
      },
      "rilievo": {
        "riferimento": "G",
        "larghezza": 98,
        "altezza": 155,
        "tipologia": "ZANZARIERA PER FINESTRA",
        "colore": "RAL 9010",
        "note": "fare attenzione durante la posa"
      }
    }
  ]
}