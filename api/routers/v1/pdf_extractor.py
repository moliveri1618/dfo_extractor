# PDF Text Extractor using PyMuPDF
import fitz  # PyMuPDF
import re
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Estrae tutto il testo da un PDF.
    
    Args:
        pdf_path: Percorso del file PDF
        
    Returns:
        Testo completo estratto
    """
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page in doc:
            text = page.get_text("text")
            text_parts.append(text)
        
        doc.close()
        return "\n\n--- PAGE BREAK ---\n\n".join(text_parts)
    except Exception as e:
        raise Exception(f"Errore nell'estrazione del PDF: {str(e)}")


def extract_text_by_pages(pdf_path: str) -> list:
    """
    Estrae il testo da un PDF, pagina per pagina.
    
    Args:
        pdf_path: Percorso del file PDF
        
    Returns:
        Lista di stringhe, una per pagina
    """
    try:
        doc = fitz.open(pdf_path)
        pages = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            pages.append({
                "page_number": page_num + 1,
                "text": text
            })
        
        doc.close()
        return pages
    except Exception as e:
        raise Exception(f"Errore nell'estrazione del PDF: {str(e)}")


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Ottiene i metadati del PDF.
    
    Args:
        pdf_path: Percorso del file PDF
        
    Returns:
        Dizionario con metadati
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = {
            "page_count": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", "")
        }
        doc.close()
        return metadata
    except Exception as e:
        raise Exception(f"Errore nella lettura dei metadati: {str(e)}")


def clean_text(text: str) -> str:
    """
    Pulisce il testo estratto rimuovendo spazi extra e caratteri problematici.
    
    Args:
        text: Testo da pulire
        
    Returns:
        Testo pulito
    """
    # Rimuovi caratteri di controllo
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalizza spazi multipli
    text = re.sub(r' +', ' ', text)
    
    # Normalizza newline multipli
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def get_page_count(pdf_path: str) -> int:
    """
    Ottiene il numero di pagine del PDF.
    
    Args:
        pdf_path: Percorso del file PDF
        
    Returns:
        Numero di pagine
    """
    try:
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except Exception as e:
        return 0
