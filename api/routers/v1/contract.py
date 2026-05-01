from fastapi import APIRouter, UploadFile, File, HTTPException, Body
import os
import uuid
import json
from datetime import datetime

from .contract_parser_v2 import ContractParserV2

router = APIRouter()

UPLOAD_FOLDER = "/tmp/uploads"
DATA_FOLDER = "/tmp/data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

contracts_db = {}


def normalize_header(header: dict):
    legacy_to_canonical = {
        "numero": "numero_contratto",
        "data": "data_contratto",
        "telefono_cliente": "cellulare_cliente",
        "azienda": "rag_sociale",
    }

    normalized = {}
    for key, value in header.items():
        normalized[legacy_to_canonical.get(key, key)] = value

    return normalized


def save_contracts_to_disk():
    index_file = os.path.join(DATA_FOLDER, "contracts_index.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(contracts_db, f, ensure_ascii=False, indent=2)


def calculate_common_fields(products):
    if not products:
        return {}

    if len(products) == 1:
        return dict(products[0])

    common = {}
    first = products[0]

    for key, value in first.items():
        if key == "Posizione":
            continue

        if all(p.get(key) == value for p in products) and value:
            common[key] = value

    return common


def calculate_summary(products):
    return {
        "total_products": len(products),
        "product_types": list(
            set(
                p.get("Tipologia Infissi", "")
                for p in products
                if p.get("Tipologia Infissi")
            )
        ),
    }


# for now simple passthrough
# later you can paste your full transform_products_for_frontend function here
def transform_products_for_frontend(products):
    return products


@router.post("/api/upload")
async def upload_contract(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome file vuoto")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo file PDF accettati")

    try:
        contract_id = str(uuid.uuid4())[:8]

        filename = f"contract_{contract_id}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file_content = await file.read()

        with open(filepath, "wb") as f:
            f.write(file_content)

        parser = ContractParserV2(filepath)
        result = parser.parse()

        contract_data = {
            "id": contract_id,
            "filename": file.filename,
            "uploaded_at": datetime.now().isoformat(),
            "filepath": filepath,
            "header": result["header"],
            "products": result["products"],
            "page_count": result["page_count"],
            "common_fields": result["common_fields"],
            "summary": result["summary"],
        }

        contracts_db[contract_id] = contract_data
        save_contracts_to_disk()

        json_path = os.path.join(DATA_FOLDER, f"contract_{contract_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(contract_data, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "contract_id": contract_id,
            "header": result["header"],
            "products_count": len(result["products"]),
            "summary": result["summary"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/contracts")
async def list_contracts():
    contracts_list = []

    for cid, data in contracts_db.items():
        header = normalize_header(data.get("header", {}))

        contracts_list.append(
            {
                "id": cid,
                "filename": data.get("filename", ""),
                "uploaded_at": data.get("uploaded_at", ""),
                "committente": header.get("committente", "N/D"),
                "numero": header.get("numero_contratto", "N/D"),
                "products_count": len(data.get("products", [])),
            }
        )

    return contracts_list


@router.get("/api/contracts/{contract_id}")
async def get_contract(contract_id: str):
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contratto non trovato")

    contract = contracts_db[contract_id]

    header = normalize_header(contract.get("header", {}))
    products = transform_products_for_frontend(contract.get("products", []))

    common_fields = {}

    if len(products) >= 2:
        field_values = {}

        for p in products:
            for key, value in p.get("fields", {}).items():
                if value:
                    field_values.setdefault(key, []).append(value)

        for key, values in field_values.items():
            if len(values) >= 2:
                try:
                    unique_values = set(str(v) for v in values)
                    if len(unique_values) == 1:
                        common_fields[key] = values[0]
                except Exception:
                    pass

    common_rilievo = {}

    avvolgibili = [
        p
        for p in products
        if p.get("articolo_info", {}).get("tipologia", "").lower() == "avvolgibile"
    ]

    if len(avvolgibili) >= 2:
        rilievo_values = {}

        for p in avvolgibili:
            rilievo = p.get("rilievo", {})
            for key, value in rilievo.items():
                if value:
                    rilievo_values.setdefault(key, []).append(value)

        for key, values in rilievo_values.items():
            if len(values) >= 2:
                try:
                    unique_values = set(str(v) for v in values)
                    if len(unique_values) == 1:
                        common_rilievo[key] = values[0]
                except Exception:
                    pass

    return {
        "id": contract_id,
        "filename": contract.get("filename", ""),
        "uploaded_at": contract.get("uploaded_at", ""),
        "header": header,
        "products": products,
        "common_fields": common_fields,
        "common_rilievo": common_rilievo,
        "summary": contract.get("summary", {}),
        "page_count": contract.get("page_count", 0),
    }


@router.put("/api/contracts/{contract_id}")
async def update_contract(contract_id: str, data: dict = Body(...)):
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contratto non trovato")

    if not data:
        raise HTTPException(status_code=400, detail="Dati non validi")

    contract = contracts_db[contract_id]

    if "header" in data:
        contract["header"].update(data["header"])

    if "products" in data:
        contract["products"] = data["products"]
        contract["common_fields"] = calculate_common_fields(contract["products"])
        contract["summary"] = calculate_summary(contract["products"])

    if "product_index" in data and "product_data" in data:
        idx = data["product_index"]
        if 0 <= idx < len(contract["products"]):
            contract["products"][idx].update(data["product_data"])

    if "product_index" in data and "rilievo" in data:
        idx = data["product_index"]
        if 0 <= idx < len(contract["products"]):
            contract["products"][idx].setdefault("rilievo", {})
            contract["products"][idx]["rilievo"].update(data["rilievo"])

    if "product_index" in data and "pezzi" in data:
        idx = data["product_index"]
        if 0 <= idx < len(contract["products"]):
            contract["products"][idx]["pezzi"] = data["pezzi"]

    contract["updated_at"] = datetime.now().isoformat()

    save_contracts_to_disk()

    json_path = os.path.join(DATA_FOLDER, f"contract_{contract_id}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(contract, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "message": "Contratto aggiornato",
        "contract_id": contract_id,
    }


@router.delete("/api/contracts/{contract_id}")
async def delete_contract(contract_id: str):
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contratto non trovato")

    contract = contracts_db[contract_id]

    pdf_path = contract.get("filepath", "")
    if pdf_path and os.path.exists(pdf_path):
        os.remove(pdf_path)

    json_path = os.path.join(DATA_FOLDER, f"contract_{contract_id}.json")
    if os.path.exists(json_path):
        os.remove(json_path)

    del contracts_db[contract_id]
    save_contracts_to_disk()

    return {
        "success": True,
        "message": "Contratto eliminato",
    }


@router.get("/api/contracts/{contract_id}/products")
async def get_contract_products(contract_id: str):
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contratto non trovato")

    contract = contracts_db[contract_id]

    return {
        "contract_id": contract_id,
        "products": contract.get("products", []),
    }


@router.get("/api/export/{contract_id}")
async def export_contract(contract_id: str):
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contratto non trovato")

    contract = contracts_db[contract_id]
    header = contract.get("header", {})
    products = contract.get("products", [])

    export_rows = []

    for i, product in enumerate(products):
        row = {
            "contratto_numero": header.get("numero", ""),
            "contratto_data": header.get("data", ""),
            "committente": header.get("committente", ""),
            "luogo_zona": header.get("luogo_zona", ""),
            "riga": i + 1,
            "quantita": product.get("articolo_info", {}).get("quantita", 1),
            "tipologia": product.get("articolo_info", {}).get("tipologia", ""),
            "misure": product.get("measures", ""),
            "riferimento_vano": product.get("riferimento_vano", ""),
            "note": product.get("note", ""),
        }

        for field_name, value in product.get("fields", {}).items():
            row[field_name] = value

        export_rows.append(row)

    return {
        "contract_id": contract_id,
        "header": header,
        "rows": export_rows,
    }
