# Contract Parser V2 - Ottimizzato per pattern "G Campo ( VALORE )"
import re
from typing import Dict, List, Any, Optional
from .pdf_extractor import extract_text_from_pdf, get_page_count


class ContractParserV2:
    """Parser ottimizzato per contratti Finstral usando pattern G Campo ( VALORE )"""

    # Pattern principale per estrarre campi
    # Usa pattern che gestisce parentesi annidate: cattura fino all'ultima ) della sequenza
    # Esempio: "G Sistema Sicurezza Infissi ( ESECUZIONE 3 (NOTTOLINI MAGGIORATI), CONTATTO Z5050 )"
    FIELD_PATTERN = re.compile(
        r"G\s+([^(]+?)\s*\(\s*((?:[^()]*|\([^()]*\))*)\s*\)", re.IGNORECASE
    )

    # Pattern per identificare inizio articolo: numero (quantità) + tipo articolo
    # Es: "5\nInfisso" o "1\nAvvolgibile"
    ARTICLE_PATTERN = re.compile(
        r"(\d+)\s*\n\s*(Infisso|Avvolgibile|Cassettoni?|Servizi?\s*accessori|Motori?|Zanzariera|Controtelaio|Portoncino|Scuro|Persiana)\s*\n",
        re.IGNORECASE,
    )

    # Tipi di articolo supportati (hanno una libreria di variabili)
    SUPPORTED_ARTICLE_TYPES = {"infisso", "avvolgibile"}

    # Mapping nomi campo -> chiavi normalizzate
    FIELD_MAPPING = {
        # Header
        "numero contratto": "numero",
        "data contratto": "data",
        "addetto": "addetto",
        "committente": "committente",
        "cf/p.iva": "cf_piva",
        "codice fiscale": "cf_piva",
        "partita iva": "cf_piva",
        "indirizzo": "indirizzo",
        "città": "citta",
        "cap": "cap",
        "cellulare": "cellulare_cliente",
        "telefono": "cellulare_cliente",
        "email": "email",
        "e-mail": "email",
        "luogo posa": "luogo_zona",
        "zona": "luogo_zona",
        "tipologia posa": "tipologia_posa",
        "consegna": "consegna",
        # Prodotto - Info base
        "tipologia": "tipologia_infissi",
        "tipologia infisso": "tipologia_infissi",
        "tipo infisso": "tipologia_infissi",
        "materiale": "materiale_infissi",
        "materiale infisso": "materiale_infissi",
        "modello": "modello_finestra",
        "modello finestra": "modello_finestra",
        "sistema": "modello_finestra",
        "fornitore": "fornitore",
        # Colori
        "colore pvc": "colore_pvc",
        "colore": "colore_pvc",
        "finitura pvc": "colore_pvc",
        "colore alluminio interno": "colore_alluminio_interno",
        "colore alluminio esterno": "colore_alluminio_esterno",
        "colore legno": "colore_legno",
        "essenza legno": "colore_legno",
        # Maniglie
        "maniglia": "maniglie_infissi",
        "maniglie": "maniglie_infissi",
        "tipo maniglia": "maniglie_infissi",
        "colore maniglia": "colore_maniglie_infissi",
        "colore maniglie": "colore_maniglie_infissi",
        "finitura maniglia": "colore_maniglie_infissi",
        # Vetro
        "vetro": "tipologia_vetro",
        "tipologia vetro": "tipologia_vetro",
        "tipo vetro": "tipologia_vetro",
        "codice vetro": "codice_vetro_infissi",
        "decoro vetro": "decoro_del_vetro",
        "canalina": "canalina_interno_vetro_infisso",
        "canalina vetro": "canalina_interno_vetro_infisso",
        "fermavetro": "fermavetro_infisso",
        # Ferramenta
        "cerniere": "cerniere_tipo",
        "tipo cerniere": "cerniere_tipo",
        "copricerniera": "copri_cerniera_finestre",
        "copri cerniera": "copri_cerniera_finestre",
        "nodo": "nodo_centrale",
        "nodo centrale": "nodo_centrale",
        "soglia": "soglia_infissi",
        "tipo soglia": "soglia_infissi",
        "guarnizione": "guarnizioni",
        "guarnizioni": "guarnizioni",
        "sicurezza": "sistema_sicurezza_infissi",
        "sistema sicurezza": "sistema_sicurezza_infissi",
        "sistema sicurezza infissi": "sistema_sicurezza_infissi",
        # Apertura
        "areazione": "areazione",
        "apertura": "areazione",
        "tipo apertura": "areazione",
        # Accessori
        "carter": "colore_carter_traslante_scorrevole_ast",
        "colore carter": "colore_carter_traslante_scorrevole_ast",
        "automazione": "kit_automazione_twin",
        "kit automazione": "kit_automazione_twin",
        "traversa": "traversa_e_pannello",
        "pannello": "traversa_e_pannello",
        "listelli": "listelli_infissi",
        "sopraluce": "sopraluce_infissi",
        "oscurante": "oscurante_infisso",
        "scuretti": "scuretti_interni",
        "modello scuretti": "modello_scuretti_interni",
        "copri cerniere scuretti": "copri_cerniere_scuretti",
        # Misure
        "larghezza": "larghezza",
        "altezza": "altezza",
        "misure": "misure",
        "dimensioni": "misure",
        "quantità": "quantita",
        "qty": "quantita",
        "pezzi": "quantita",
        # Riferimento
        "riferimento": "riferimento_vano",
        "vano": "riferimento_vano",
        "posizione": "riferimento_vano",
        "locale": "riferimento_vano",
        # Note
        "note": "note",
        "nota": "note",
        "annotazioni": "note",
        "responsabilità": "responsabilita",
        "responsabilita": "responsabilita",
        # Avvolgibili
        "materiale avvolgibile": "avv_contratto_materiale_avvolgibili",
        "materiale avvolgibili": "avv_contratto_materiale_avvolgibili",
        "tipo avvolgibile": "avv_contratto_materiale_avvolgibili",
        "colore avvolgibile": "avv_contratto_colori_avvolgibili",
        "colore avvolgibili": "avv_contratto_colori_avvolgibili",
        "guida": "avv_contratto_guida_avvolgibile",
        "guida avvolgibile": "avv_contratto_guida_avvolgibile",
        "colore guida": "avv_contratto_colore_guida_avvolgibile",
        "colore guida avvolgibile": "avv_contratto_colore_guida_avvolgibile",
        "terminale": "avv_contratto_terminale",
        "accessori": "avv_contratto_accessori_avvolgibili",
        "accessori avvolgibile": "avv_contratto_accessori_avvolgibili",
        "accessori avvolgibili": "avv_contratto_accessori_avvolgibili",
        "fornitore avvolgibili": "avv_contratto_fornitore",
    }

    # Campi header (testata contratto) - nomi canonici
    HEADER_FIELDS = {
        "numero_contratto",
        "data_contratto",
        "addetto",
        "committente",
        "cf_piva",
        "indirizzo",
        "citta",
        "cap",
        "cellulare_cliente",
        "email",
        "luogo_zona",
        "tipologia_posa",
        "consegna",
    }

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.raw_text = extract_text_from_pdf(pdf_path)
        self.page_count = get_page_count(pdf_path)
        self.header = {}
        self.products = []

    def parse(self) -> Dict[str, Any]:
        """Parsing completo del contratto"""
        # Estrai header dalla prima sezione (formato CHIAVE\nVALORE)
        self._extract_header()

        # Estrai tutti i campi con pattern G
        all_fields = self._extract_all_fields()

        # Estrai prodotti dai campi G
        self._extract_products_from_fields(all_fields)

        # Calcola campi comuni
        common_fields = self.get_common_fields()

        # Calcola summary
        summary = self._calculate_summary()

        return {
            "header": self.header,
            "products": self.products,
            "common_fields": common_fields,
            "summary": summary,
            "page_count": self.page_count,
            "raw_text": self.raw_text[:5000],  # Solo primi 5000 caratteri per debug
        }

    def _extract_header(self):
        """Estrae i dati della testata dal formato CHIAVE\\nVALORE"""
        # Mapping dei campi header nel formato del PDF
        header_patterns = {
            "NUMERO": "numero_contratto",
            "DATA": "data_contratto",
            "ADDETTO": "addetto",
            "COMMITTENTE": "committente",
            "CF / P.IVA": "cf_piva",
            "CF/P.IVA": "cf_piva",
            "INDIRIZZO": "indirizzo",
            "CITTÀ": "citta",
            "CAP": "cap",
            "CELLULARE": "cellulare_cliente",
            "TELEFONO": "telefono_cliente",
            "EMAIL": "email",
            "LUOGO / ZONA": "luogo_zona",
            "LUOGO/ZONA": "luogo_zona",
            "TIPOLOGIA DI POSA IN OPERA": "tipologia_posa",
            "CONSEGNA": "consegna",
            "FATTURAZIONE ELETTRONICA / PEC": "sdi_pec",
            "ALTRI CONTATTI": "altri_contatti",
            "CONTATTO PROGETTO": "contatto_progetto",
            "ARCHITETTO": "architetto",
            "CONTATTO IMPRESA EDILE": "contatto_impresa_edile",
        }

        # Estrai la prima sezione (prima di "ARTICOLI")
        header_section = (
            self.raw_text.split("ARTICOLI")[0]
            if "ARTICOLI" in self.raw_text
            else self.raw_text[:2000]
        )

        lines = header_section.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Cerca match con le chiavi header
            for key_pattern, field_name in header_patterns.items():
                if line == key_pattern or line.startswith(key_pattern):
                    # Il valore è nella riga successiva
                    if i + 1 < len(lines):
                        value = lines[i + 1].strip()
                        # Evita di prendere un'altra chiave come valore
                        if value and value not in header_patterns:
                            self.header[field_name] = value
                            i += 1  # Salta la riga del valore
                    break
            i += 1

        # Estrai anche il nome progetto/riferimento se presente nel committente o indirizzo
        if "committente" in self.header:
            self.header["nome_progetto"] = self.header["committente"]

        # Estrai ragione sociale dal logo/intestazione (top-left del contratto)
        header_upper = header_section.upper()
        if "TIGULLIO" in header_upper:
            self.header["rag_sociale"] = "Tigullio Design SRL"
        elif (
            "FINESTRE ANTIRUMORE" in header_upper
            or "FINESTREANTIRUMORE" in header_upper
        ):
            self.header["rag_sociale"] = "Finestre Antirumore SRL"
        else:
            self.header["rag_sociale"] = ""

    def _extract_all_fields(self) -> List[Dict[str, str]]:
        """Estrae tutti i campi dal testo usando il pattern G Campo ( VALORE )"""
        fields = []

        for match in self.FIELD_PATTERN.finditer(self.raw_text):
            field_name = match.group(1).strip().lower()
            field_value = match.group(2).strip()

            # Normalizza il nome campo
            normalized_key = self._normalize_field_name(field_name)

            # Gestisce valori multipli separati da virgola
            # Es: "ESECUZIONE 3 (NOTTOLINI MAGGIORATI), CONTATTO MAGNETICO ALLARME Z5050"
            # Diventa: "ESECUZIONE 3 (NOTTOLINI MAGGIORATI)\nCONTATTO MAGNETICO ALLARME Z5050"
            if "," in field_value:
                # Split sui valori e normalizza
                parts = [p.strip() for p in field_value.split(",") if p.strip()]
                if len(parts) > 1:
                    field_value = "\n".join(parts)

            if normalized_key:
                fields.append(
                    {
                        "original_name": field_name,
                        "key": normalized_key,
                        "value": field_value,
                        "position": match.start(),
                    }
                )

        return fields

    def _normalize_field_name(self, field_name: str) -> Optional[str]:
        """Normalizza il nome del campo usando il mapping"""
        field_name = field_name.lower().strip()

        # Cerca match esatto
        if field_name in self.FIELD_MAPPING:
            return self.FIELD_MAPPING[field_name]

        # Cerca match parziale
        for pattern, key in self.FIELD_MAPPING.items():
            if pattern in field_name or field_name in pattern:
                return key

        # Se non trovato, crea una chiave dal nome
        return field_name.replace(" ", "_").replace("-", "_")

    def _extract_products_from_fields(self, all_fields: List[Dict[str, str]]):
        """Estrae i prodotti dal testo usando il pattern Articolo

        Estrae SOLO articoli di tipo supportato (Infisso, Avvolgibile).
        Struttura nel PDF:
            QUANTITÀ
            5
            Infisso
            G Fornitore ( ... )
            G Tipologia Infissi ( ... )
            ...
        """
        # Prima trova tutti gli articoli nel testo
        articles = self._find_all_articles()

        # Per ogni articolo supportato, estrai i campi G associati
        for article in articles:
            article_type = article["type"].lower()

            # Salta articoli non supportati
            if article_type not in self.SUPPORTED_ARTICLE_TYPES:
                continue

            # Trova i campi G che appartengono a questo articolo
            # (tra la posizione di questo articolo e il prossimo)
            start_pos = article["position"]
            end_pos = article.get("end_position", len(self.raw_text))

            # Estrai i campi G in questo range
            product_fields = [
                f for f in all_fields if start_pos <= f["position"] < end_pos
            ]

            if not product_fields:
                continue

            # Crea il prodotto con chiavi canoniche snake_case
            product = {
                "posizione": len(self.products) + 1,
                "quantita": article["quantity"],
                "tipo_articolo": article["type"],  # Infisso o Avvolgibile
            }

            # Estrai riferimento vano dalle righe G senza parentesi
            riferimento = self._extract_riferimento_from_range(start_pos, end_pos)
            if riferimento:
                product["riferimento_vano"] = riferimento

            # Aggiungi tutti i campi con chiavi canoniche snake_case
            for field in product_fields:
                canonical_key = self._get_display_name(field["key"])
                product[canonical_key] = field["value"]

            # Estrai eventuali note non strutturate
            notes = self._extract_notes_from_range(start_pos, end_pos)
            if notes:
                product["note"] = notes

            self._finalize_product(product)
            self.products.append(product)

    def _find_all_articles(self) -> List[Dict[str, Any]]:
        """Trova tutti gli articoli nel testo con posizione, quantità e tipo"""
        articles = []

        # Pattern per trovare: numero\nTipoArticolo
        # Es: "5\nInfisso" o "1\nAvvolgibile"
        for match in self.ARTICLE_PATTERN.finditer(self.raw_text):
            quantity = int(match.group(1))
            article_type = match.group(2).strip()
            position = match.end()  # Posizione dopo il tipo articolo

            articles.append(
                {
                    "quantity": quantity,
                    "type": article_type,
                    "position": position,
                    "match_start": match.start(),
                }
            )

        # Calcola end_position per ogni articolo (fino al prossimo articolo o fine sezione)
        for i, article in enumerate(articles):
            if i + 1 < len(articles):
                article["end_position"] = articles[i + 1]["match_start"]
            else:
                # Ultimo articolo: cerca fine sezione (prezzi, totali, etc.)
                article["end_position"] = self._find_products_end(article["position"])

        return articles

    def _extract_riferimento_from_range(self, start_pos: int, end_pos: int) -> str:
        """Estrae il riferimento vano dalle righe G che iniziano con RIF. (es: G RIF.A-C-D-G-I)

        IMPORTANTE: Cattura SOLO la riga del RIF., non le righe successive che sono note.
        Esempio:
            G RIF.H (BAGNO)              <- Questo è il riferimento
            G Posa con arretramento...   <- Questa è una nota, NON parte del riferimento
        """
        text_section = self.raw_text[start_pos:end_pos]

        # Pattern per righe G che iniziano con RIF - cattura solo fino a fine riga
        # Esempio: "G RIF.A-C-D-G-I" oppure "G RIF.H (BAGNO)"
        rif_pattern = re.compile(r"G\s+(RIF\.[^\n]+)", re.IGNORECASE)

        riferimenti = []
        for match in rif_pattern.finditer(text_section):
            rif = match.group(1).strip()
            # Pulisci spazi multipli
            rif = re.sub(r"\s+", " ", rif)
            riferimenti.append(rif)

        return " / ".join(riferimenti) if riferimenti else ""

    def _extract_notes_from_range(self, start_pos: int, end_pos: int) -> str:
        """Estrae note non strutturate da un range di testo"""
        text_section = self.raw_text[start_pos:end_pos]

        # Trova righe G senza parentesi che non sono riferimenti
        # Es: "G Posa con arretramento per zanzariere"
        note_pattern = re.compile(r"G\s+([^(]+?)(?:\n|$)", re.IGNORECASE)

        notes = []
        for match in note_pattern.finditer(text_section):
            note_text = match.group(1).strip()
            # Ignora se è un riferimento
            if note_text.upper().startswith("RIF"):
                continue
            # Ignora se è troppo corto
            if len(note_text) < 5:
                continue
            # Ignora se sembra un campo con parentesi non catturato
            if "(" in note_text:
                continue
            notes.append(note_text)

        return " | ".join(notes) if notes else ""

    def _extract_notes_between(self, start_pos: int, end_pos: int) -> str:
        """Estrae note non strutturate tra due posizioni nel testo"""
        if start_pos >= end_pos or start_pos >= len(self.raw_text):
            return ""

        text_section = self.raw_text[start_pos:end_pos]

        # Rimuovi pattern G Campo ( VALORE ) residui
        cleaned = self.FIELD_PATTERN.sub("", text_section)

        # Pulisci e filtra le righe
        lines = []
        for line in cleaned.split("\n"):
            line = line.strip()
            # Ignora righe vuote, numeri soli, o righe troppo corte
            if not line or len(line) < 3:
                continue
            # Ignora righe che sono solo numeri o simboli
            if re.match(r"^[\d\s\.\,\-\(\)]+$", line):
                continue
            # Ignora righe che sembrano intestazioni tecniche
            if line.upper() in ["ARTICOLI", "TOTALE", "IVA", "IMPONIBILE"]:
                continue
            # Ignora parole singole molto corte
            if len(line) < 4 and not line.isupper():
                continue
            lines.append(line)

        # Unisci le note trovate
        notes = " - ".join(lines)

        # Limita lunghezza
        if len(notes) > 500:
            notes = notes[:500] + "..."

        return notes

    def _find_products_end(self, from_pos: int) -> int:
        """Trova la fine della sezione prodotti"""
        # Cerca indicatori di fine sezione
        end_markers = [
            "TOTALE IMPONIBILE",
            "IVA COMPRESA",
            "CONDIZIONI",
            "PAGAMENTO",
            "FIRMA",
        ]

        end_pos = len(self.raw_text)
        for marker in end_markers:
            idx = self.raw_text.upper().find(marker, from_pos)
            if idx != -1 and idx < end_pos:
                end_pos = idx

        return end_pos

    def _finalize_product(self, product: Dict):
        """Finalizza un prodotto assicurandosi che abbia tutti i campi necessari"""
        # Assicura che ci sia la posizione
        if "posizione" not in product:
            product["posizione"] = 1

    def _get_display_name(self, key: str) -> str:
        """Restituisce la chiave canonica snake_case.

        NOTA: Non converte più in Title Case.
        Usa field_definitions.CANONICAL_TO_LABEL per le label di visualizzazione.
        """
        # Ritorna direttamente la chiave canonica snake_case
        return key

    def _create_products_from_text(self):
        """Crea prodotti analizzando il testo quando il pattern G non funziona bene"""
        # Pattern alternativo per trovare sezioni prodotto
        # Cerca pattern come "FINESTRA", "PORTA FINESTRA", ecc.
        product_patterns = [
            r"(FINESTRA\s+\d+\s+ANT[AE])",
            r"(PORTA\s+FINESTRA\s+\d+\s+ANT[AE])",
            r"(FISSO)",
            r"(HST\s+\d+\s+ANT[AE])",
            r"(AST\s+\d+\s+ANT[AE])",
            r"(CONTROTELAIO)",
        ]

        for pattern in product_patterns:
            matches = re.finditer(pattern, self.raw_text, re.IGNORECASE)
            for match in matches:
                tipologia = match.group(1).strip()
                product = {
                    "articolo_info": {"tipologia": tipologia, "quantita": 1},
                    "fields": {"fornitore": "Finstral"},
                    "riferimento_vano": "",
                    "measures": "",
                    "note": "",
                }
                self.products.append(product)

        # Rimuovi duplicati basati sulla posizione nel testo
        # (implementazione semplificata)

    def get_common_fields(self) -> Dict[str, str]:
        """
        Trova i campi che hanno lo stesso valore in tutti i prodotti.
        Un campo è comune se:
        1. È presente in almeno 2 prodotti
        2. Ha lo stesso valore in TUTTI i prodotti che lo contengono
        """
        if len(self.products) < 2:
            return {}

        # Raccogli tutti i valori per ogni campo
        field_values = {}
        for product in self.products:
            for key, value in product.get("fields", {}).items():
                if value:  # Ignora valori vuoti
                    if key not in field_values:
                        field_values[key] = []
                    field_values[key].append(value)

        # Trova campi comuni
        common = {}
        for key, values in field_values.items():
            if len(values) >= 2:  # Presente in almeno 2 prodotti
                unique_values = set(values)
                if len(unique_values) == 1:  # Tutti uguali
                    common[key] = values[0]

        return common

    def _calculate_summary(self) -> Dict[str, Any]:
        """Calcola statistiche riassuntive"""
        total_qty = sum(
            p.get("articolo_info", {}).get("quantita", 1) for p in self.products
        )

        by_tipologia = {}
        by_materiale = {}
        by_modello = {}

        for p in self.products:
            qty = p.get("articolo_info", {}).get("quantita", 1)
            tipologia = p.get("articolo_info", {}).get("tipologia", "N/D")
            materiale = p.get("fields", {}).get("materiale_infissi", "N/D")
            modello = p.get("fields", {}).get("modello_finestra", "N/D")

            by_tipologia[tipologia] = by_tipologia.get(tipologia, 0) + qty
            if materiale != "N/D":
                by_materiale[materiale] = by_materiale.get(materiale, 0) + qty
            if modello != "N/D":
                by_modello[modello] = by_modello.get(modello, 0) + qty

        return {
            "total_products": len(self.products),
            "total_quantity": total_qty,
            "by_tipologia": by_tipologia,
            "by_materiale": by_materiale,
            "by_modello": by_modello,
        }
