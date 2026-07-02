# Servidor mínimo para servir los datos GTFS al visor
# Solo necesita: python3 -m http.server 8080 (ya lo hace iniciar.bat)
# Este archivo es el endpoint que lista los ZIPs disponibles

import os
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def list_zips():
    """Devuelve lista de ZIPs en data/ con sus tamaños"""
    if not DATA_DIR.exists():
        return []
    
    zips = []
    for f in sorted(DATA_DIR.glob("*.zip")):
        zips.append({
            "name": f.name,
            "size": f.stat().st_size,
            "size_human": f"{f.stat().st_size / 1024 / 1024:.1f} MB"
        })
    return zips

if __name__ == "__main__":
    # Modo standalone: imprimir lista
    zips = list_zips()
    print(json.dumps(zips, indent=2))
    print(f"\nTotal: {len(zips)} ZIPs, {sum(z['size'] for z in zips) / 1024 / 1024:.1f} MB")
