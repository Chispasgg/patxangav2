#!/usr/bin/env python3
"""
Renombra los archivos de fotos/ a formato consecutivo (0.ext, 1.ext, ...)
y actualiza las referencias en config/config.json.
"""

import json
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
FOTOS_DIR = BASE_DIR / "fotos"
CONFIG_PATH = BASE_DIR / "config" / "config.json"

def main():
    # 1. Listar todos los archivos en fotos/, separar imágenes de videos
    all_files = sorted(FOTOS_DIR.iterdir(), key=lambda p: p.name.lower())
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    video_exts = {'.mov', '.mp4', '.avi', '.webm', '.mkv'}

    image_files = [f for f in all_files if f.suffix.lower() in image_exts]
    video_files = [f for f in all_files if f.suffix.lower() in video_exts]
    other_files = [f for f in all_files if f.suffix.lower() not in image_exts | video_exts]

    if other_files:
        print(f"⚠ Archivos ignorados (extensión no reconocida): {[f.name for f in other_files]}")

    # 2. Construir el mapeo: stem_antiguo → número_nuevo (todos juntos)
    all_to_rename = image_files + video_files
    stem_to_new = {}
    for i, fpath in enumerate(all_to_rename):
        stem_to_new[fpath.stem] = i

    print(f"Total archivos a renombrar: {len(all_to_rename)} "
          f"({len(image_files)} imágenes + {len(video_files)} vídeos)")

    # 3. Cargar config.json
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    images_in_json = config['items'][2]['images']

    # 4. Detectar stems en JSON que no tienen archivo y stems de archivos sin JSON
    json_stems = {img['name'] for img in images_in_json}
    file_stems = {f.stem for f in all_to_rename}

    only_json = json_stems - file_stems
    only_files = file_stems - json_stems

    print(f"\nDiscrepancias encontradas:")
    print(f"  En JSON sin archivo: {sorted(only_json)}")
    print(f"  En archivos sin JSON: {sorted(only_files)}")

    # 5. Construir mapeo entre stems huérfanos de JSON ↔ archivos sin JSON
    # Los ordenamos y los emparejamos posicionalmente (asumiendo 1-a-1)
    orphan_json = sorted(only_json)
    orphan_files = sorted(only_files)
    if len(orphan_json) != len(orphan_files):
        print(f"⚠ Número de huérfanos no coincide: {len(orphan_json)} JSON vs {len(orphan_files)} archivos")
        print("   Continuando sin mapear huérfanos...")
        json_to_file_stem = {}
    else:
        json_to_file_stem = dict(zip(orphan_json, orphan_files))
        print(f"\nMapeo de huérfanos: {json_to_file_stem}")

    # 6. Actualizar nombres en config.json
    updated = 0
    not_found = []
    for img in images_in_json:
        old_name = img['name']
        # Buscar el stem real del archivo (puede ser directo o vía mapeo de huérfanos)
        real_stem = json_to_file_stem.get(old_name, old_name)
        if real_stem in stem_to_new:
            new_name = str(stem_to_new[real_stem])
            img['name'] = new_name
            updated += 1
        else:
            not_found.append(old_name)

    if not_found:
        print(f"\n⚠ Entradas JSON sin archivo correspondiente: {not_found}")

    # 7. Renombrar archivos en el sistema de ficheros (usando nombres temporales para evitar colisiones)
    print(f"\nRenombrando archivos...")
    tmp_suffix = "__tmp__"
    rename_map = []  # (old_path, new_path)
    for fpath in all_to_rename:
        new_num = stem_to_new[fpath.stem]
        new_name = f"{new_num}{fpath.suffix}"
        new_path = FOTOS_DIR / new_name
        rename_map.append((fpath, new_path))

    # Paso 1: renombrar a temporales para evitar colisiones (ej: 0.jpg → 1.jpg cuando 1.jpg ya existe)
    tmp_paths = []
    for old_path, new_path in rename_map:
        tmp_path = old_path.with_name(old_path.name + tmp_suffix)
        old_path.rename(tmp_path)
        tmp_paths.append((tmp_path, new_path))

    # Paso 2: renombrar de temporales a nombres finales
    for tmp_path, new_path in tmp_paths:
        tmp_path.rename(new_path)
        print(f"  {tmp_path.name.replace(tmp_suffix,'')} → {new_path.name}")

    # 8. Guardar config.json actualizado
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Renombrados {len(rename_map)} archivos")
    print(f"✓ Actualizadas {updated} entradas en config.json")
    if not_found:
        print(f"⚠ {len(not_found)} entradas JSON no actualizadas: {not_found}")

if __name__ == "__main__":
    main()
