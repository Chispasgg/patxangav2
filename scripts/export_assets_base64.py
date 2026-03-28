#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import mimetypes
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".svg",
    ".mp4",
    ".webm",
    ".mov",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convierte los archivos de assets a base64 y genera un .txt por archivo "
            "en el directorio de salida."
        )
    )
    parser.add_argument(
        "--input-dir",
        default="assets",
        help="Directorio con imágenes y vídeos a exportar. Por defecto: assets",
    )
    parser.add_argument(
        "--output-dir",
        default="base64_exports",
        help="Directorio donde se generarán los .txt. Por defecto: base64_exports",
    )
    parser.add_argument(
        "--include-data-url",
        action="store_true",
        help="Genera el contenido como data URL completa en lugar de base64 puro.",
    )
    return parser.parse_args()


def iter_asset_files(input_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def encode_file(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def build_output_content(path: Path, include_data_url: bool) -> str:
    encoded = encode_file(path)

    if not include_data_url:
        return encoded

    mime_type, _ = mimetypes.guess_type(path.name)
    resolved_mime_type = mime_type or "application/octet-stream"
    return f"data:{resolved_mime_type};base64,{encoded}"


def export_assets(input_dir: Path, output_dir: Path, include_data_url: bool) -> int:
    if not input_dir.exists():
      raise FileNotFoundError(f"No existe el directorio de entrada: {input_dir}")

    if not input_dir.is_dir():
      raise NotADirectoryError(f"La ruta de entrada no es un directorio: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    assets = iter_asset_files(input_dir)

    for asset in assets:
        output_path = output_dir / f"{asset.stem}.txt"
        output_content = build_output_content(asset, include_data_url)
        output_path.write_text(output_content, encoding="utf-8")

    return len(assets)


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    exported_count = export_assets(input_dir, output_dir, args.include_data_url)

    if exported_count == 0:
        print(f"No se han encontrado archivos compatibles en {input_dir}")
        return 0

    print(
        f"Exportados {exported_count} archivos desde {input_dir} a {output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
