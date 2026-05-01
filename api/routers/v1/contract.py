from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
from datetime import datetime
from .contract_parser_v2 import ContractParserV2

router = APIRouter()

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

        return {
            "success": True,
            "contract_id": contract_id,
            "header": result["header"],
            "products_count": len(result["products"]),
            "summary": result["summary"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
