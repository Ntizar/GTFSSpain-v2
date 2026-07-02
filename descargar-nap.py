#!/usr/bin/env python3
"""
Descarga completa de todos los datos NAP (Nodo de Acceso al Transporte Público)
- Metadatos de todos los conjuntos de datos
- Ficheros GTFS actuales (ZIP)
- Estructura optimizada para git

Uso:
  python3 descargar-nap.py           # Descarga completa
  python3 descargar-nap.py --delta   # Solo actualizados (delta)
  python3 descargar-nap.py --dry-run # Solo muestra qué se descargaría

Requiere:
  - NAP_API_KEY en /root/workspace/TimeIneco/.env o como variable de entorno
  - curl instalado
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Configuración
BASE_DIR = Path("/root/workspace/GTFSSpain")
API_BASE = "https://nap.transportes.gob.es"
OUTPUT_DIR = BASE_DIR / "data"
METADATA_FILE = BASE_DIR / "metadata" / "conjuntos-datos.json"
TIMESTAMP_FILE = BASE_DIR / "metadata" / "ultima-descarga.txt"
LOG_FILE = BASE_DIR / "metadata" / "descarga.log"

# Rutas de los datasets que se actualizaron (para delta)
UPDATED_IDS_FILE = BASE_DIR / "metadata" / "ids-actualizados.json"


def get_api_key():
    """Obtiene la API key de NAP."""
    # 1. Variable de entorno
    key = os.environ.get("NAP_API_KEY")
    if key:
        return key

    # 2. Desde .env de TimeIneco o Time
    env_paths = [
        "/root/workspace/TimeIneco/.env",
        "/root/workspace/Time/.env",
        "/root/.env",
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("NAP_API_KEY="):
                        return line.strip().split("=", 1)[1]

    print("❌ Error: No se encontró NAP_API_KEY")
    print("   Configura en: /root/workspace/TimeIneco/.env")
    sys.exit(1)


def api_get(endpoint):
    """Hace una petición GET a la API de NAP."""
    key = get_api_key()
    result = subprocess.run(
        ["curl", "-s", "-H", f"ApiKey: {key}", "--max-time", "60",
         f"{API_BASE}{endpoint}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ❌ Error API: {result.stderr[:200]}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ❌ JSON inválido: {result.stdout[:200]}")
        return None


def log(msg):
    """Escribe en log y stdout."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def download_file(file_id, output_path):
    """Descarga un fichero GTFS desde NAP."""
    # Obtener enlace de descarga
    result = api_get(f"/api/v2/fichero/{file_id}/descarga")
    if not result or not result.get("data"):
        return False

    download_url = result["data"].get("enlaceDescarga")
    if not download_url:
        return False

    # Descargar con curl
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "300",
         "-o", str(output_path), download_url],
        capture_output=True, text=True
    )
    return result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0


def descargar_completa(delta=False):
    """Descarga todos los conjuntos de datos o solo los actualizados."""
    log("=" * 60)
    log("INICIO DESCARGA NAP")
    log(f"Modo: {'DELTA' if delta else 'COMPLETA'}")

    # Crear estructura de directorios
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Obtener todos los conjuntos de datos
    log("Obteniendo metadatos de la API...")
    data = api_get("/api/v2/conjunto-dato")
    if not data:
        log("❌ No se pudieron obtener los metadatos")
        sys.exit(1)

    conjuntos = data.get("data", [])
    log(f"Total conjuntos: {len(conjuntos)}")

    # Cargar IDs ya descargados
    prev_ids = set()
    if UPDATED_IDS_FILE.exists():
        with open(UPDATED_IDS_FILE, "r") as f:
            prev_ids = set(json.load(f).get("ids", []))

    # Determinar qué descargar
    to_download = []
    skip_count = 0
    for c in conjuntos:
        cid = c["id"]
        if delta and cid in prev_ids:
            # En modo delta, verificar si hay actualización
            # Comprobar fichero más reciente
            ficheros = c.get("ficheros", [])
            if not ficheros:
                continue
            # Ordenar por fecha de actualización
            ficheros_sorted = sorted(ficheros, key=lambda f: f.get("fechaActualizacion", ""), reverse=True)
            last_update = ficheros_sorted[0].get("fechaActualizacion", "")
            # Si se actualizó hoy o ayer, descargar
            if last_update:
                try:
                    from datetime import datetime, timedelta
                    last_dt = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    if (now - last_dt).days <= 1:
                        to_download.append(c)
                    else:
                        skip_count += 1
                except:
                    to_download.append(c)
            else:
                skip_count += 1
        else:
            to_download.append(c)

    log(f"A descargar: {len(to_download)} | Saltar: {skip_count}")

    # Descargar cada conjunto
    total_size = 0
    success_count = 0
    failed_count = 0
    current_ids = set()

    for i, c in enumerate(to_download, 1):
        cid = c["id"]
        nombre = c.get("nombre", f"dataset-{cid}")
        # Nombre de carpeta seguro
        folder_name = f"{cid:05d}_{nombre.replace('/', '_').replace('\\\\', '_')[:80]}"
        dataset_dir = OUTPUT_DIR / folder_name

        # Crear carpeta
        dataset_dir.mkdir(parents=True, exist_ok=True)
        current_ids.add(cid)

        # Guardar metadatos del conjunto
        meta_file = dataset_dir / "metadata.json"
        with open(meta_file, "w") as f:
            json.dump(c, f, indent=2, ensure_ascii=False)

        # Descargar ficheros
        ficheros = c.get("ficheros", [])
        for fi in ficheros:
            file_id = fi.get("id")
            file_size = fi.get("tamanio", 0)
            file_name = fi.get("nombreTipoFichero", "fichero")
            file_date = fi.get("fechaActualizacion", "")

            # Nombre del fichero
            safe_name = f"{file_id}_{file_name.replace('/', '_')}.zip"
            output_path = dataset_dir / safe_name

            # Skip si ya existe y es delta (optimización)
            if delta and output_path.exists() and output_path.stat().st_size > 0:
                # Verificar si es la misma versión
                if file_date:
                    try:
                        from datetime import datetime, timedelta
                        last_dt = datetime.fromisoformat(file_date.replace("Z", "+00:00"))
                        now = datetime.now(timezone.utc)
                        if (now - last_dt).days > 1:
                            continue  # No actualizado
                    except:
                        pass

            log(f"  [{i}/{len(to_download)}] {nombre[:50]:50s} | {file_name:15s} | {file_size/1024/1024:6.1f} MB")

            if download_file(file_id, output_path):
                actual_size = output_path.stat().st_size
                total_size += actual_size
                success_count += 1
                log(f"    ✅ {actual_size/1024/1024:.1f} MB descargados")
            else:
                failed_count += 1
                log(f"    ❌ Error descargando")

        # Pausa entre datasets para no saturar la API
        time.sleep(0.5)

    # Guardar estado
    UPDATED_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(UPDATED_IDS_FILE, "w") as f:
        json.dump({"ids": list(current_ids), "fecha": datetime.now(timezone.utc).isoformat()}, f, indent=2)

    TIMESTAMP_FILE.write_text(datetime.now(timezone.utc).isoformat())

    # Resumen
    log("=" * 60)
    log("RESUMEN")
    log(f"  Éxitos: {success_count}")
    log(f"  Fallos: {failed_count}")
    log(f"  Total descargado: {total_size/1024/1024/1024:.2f} GB")
    log(f"  Conjuntos: {len(current_ids)}/{len(conjuntos)}")
    log("=" * 60)

    return success_count > 0


if __name__ == "__main__":
    mode = "completa"
    if "--delta" in sys.argv:
        mode = "delta"
    elif "--dry-run" in sys.argv:
        print("Modo dry-run: no se descargará nada")
        print("Muestra qué se descargaría")
        key = get_api_key()
        data = api_get("/api/v2/conjunto-dato")
        if data:
            conjuntos = data["data"]
            print(f"Total conjuntos: {len(conjuntos)}")
            total_size = sum(
                sum(f.get("tamanio", 0) for f in c.get("ficheros", []))
                for c in conjuntos
            )
            print(f"Tamaño total: {total_size/1024/1024/1024:.2f} GB")
        sys.exit(0)

    delta = mode == "delta"
    descargar_completa(delta=delta)
