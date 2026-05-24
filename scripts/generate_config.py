#!/usr/bin/env python3
"""
Genera config/config.json con todos los archivos de base64_exports como items.
Extrae fechas de los nombres de archivo cuando es posible.
"""

import json
import os
import re
import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
EXPORTS_DIR = BASE_DIR / "base64_exports"
CONFIG_PATH = BASE_DIR / "config" / "config.json"

MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
}

# Prefijos base64 conocidos para detectar mime type
MIME_PREFIXES = {
    "/9j/":     "image/jpeg",
    "iVBORw0":  "image/png",
    "R0lGOD":   "image/gif",
    "UklGR":    "image/webp",
    "AAAA":     "video/mp4",   # ftyp MP4
    "AAAM":     "video/mp4",
    "GkXf":     "video/webm",
}

def detect_mime(b64_content: str) -> str:
    prefix = b64_content[:8]
    for k, v in MIME_PREFIXES.items():
        if prefix.startswith(k):
            return v
    return "image/jpeg"  # fallback


def extract_date(stem: str) -> str:
    """Intenta extraer una fecha YYYY-MM-DD del nombre de archivo (sin extensión)."""

    # 1. YYYY-MM-DD al inicio (ej: "2010-04-17 15-18-29", "2011-01-03 16-43-37")
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', stem)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 2. YYYYMMDD_HHMMSS (ej: "20190308_132909")
    m = re.match(r'^(\d{4})(\d{2})(\d{2})_\d+$', stem)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 3. IMG_YYYYMMDD_HHMMSS (ej: "IMG_20230402_033617")
    m = re.match(r'^IMG_(\d{4})(\d{2})(\d{2})_\d+$', stem, re.IGNORECASE)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 4. IMG-YYYYMMDD-WANNN (ej: "IMG-20190318-WA0007")
    m = re.match(r'^IMG-(\d{4})(\d{2})(\d{2})-', stem, re.IGNORECASE)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 5. DDMMYYYY### (ej: "10042010045", "27012010017", "13012009132")
    m = re.match(r'^(\d{2})(\d{2})(\d{4})\d+$', stem)
    if m:
        dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
        if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
            return f"{yyyy}-{mm}-{dd}"

    # 6. YYYY_mes_N (ej: "2010_abril_3") o YYYY_mes (ej: "2008_agosto")
    m = re.match(r'^(\d{4})_([a-z]+)(?:_(\d+))?$', stem, re.IGNORECASE)
    if m:
        yyyy = m.group(1)
        mes_str = m.group(2).lower()
        day_num = int(m.group(3)) if m.group(3) else 1
        mm = MESES.get(mes_str)
        if mm:
            return f"{yyyy}-{mm}-{day_num:02d}"

    # 7. JEXY_DDMMYY-HHMMSS (ej: "JEXY_110319-121611")
    m = re.match(r'^JEXY_(\d{2})(\d{2})(\d{2})-', stem, re.IGNORECASE)
    if m:
        dd, mm, yy = m.group(1), m.group(2), m.group(3)
        yyyy = f"20{yy}" if int(yy) < 50 else f"19{yy}"
        if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
            return f"{yyyy}-{mm}-{dd}"

    return "YYYY-MM-DD"


def mime_to_type(mime: str) -> str:
    if mime.startswith("video"):
        return "video"
    return "image"


def main():
    # Leer config existente (aunque esté malformado, preservamos los campos conocidos)
    existing = {
        "pageTitle": "Patxanga QR",
        "title": "Taj's bitches",
        "description": "Sexcurity is coming",
        "timeMode": "utc",
        "defaultItem": {
            "name": "Pólvoraaaa!!",
            "description": "Se vienen cositas...",
            "type": "image",
            "img": "",
        },
    }

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = f.read()
        loaded = json.loads(raw)
        existing.update(loaded)
    except Exception:
        print("⚠  config.json no era JSON válido; usando valores por defecto.")

    # Construir items
    items = []
    files = sorted(EXPORTS_DIR.glob("*.txt"))
    print(f"Procesando {len(files)} archivos...")

    for fpath in files:
        stem = fpath.stem
        b64 = fpath.read_text(encoding="utf-8").strip()
        mime = detect_mime(b64)
        item_type = mime_to_type(mime)
        date = extract_date(stem)

        item = {
            "date": date,
            "name": stem,
            "type": item_type,
            "mimeType": mime,
        }
        items.append(item)
        date_label = date if date != "YYYY-MM-DD" else "⚠ sin fecha"
        print(f"  {stem:40s}  {date_label}  [{item_type}]")

    existing["items"] = items

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    size_mb = CONFIG_PATH.stat().st_size / 1024 / 1024
    print(f"\n✓ config.json generado con {len(items)} items ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
