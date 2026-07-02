#!/bin/bash
# Cron job: actualizar GTFSSpain semanalmente
# Se ejecuta cada domingo a las 06:00 UTC

set -e

LOG="/root/workspace/GTFSSpain/metadata/cron-log.txt"
REPO="/root/workspace/GTFSSpain"

echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] INICIO cron GTFSSpain" >> "$LOG"

# Verificar que existe el repo
if [ ! -d "$REPO" ]; then
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] ERROR: Repo no existe" >> "$LOG"
    exit 1
fi

cd "$REPO"

# Descargar delta (solo actualizados)
python3 descargar-nap.py --delta >> "$LOG" 2>&1
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] ÉXITO" >> "$LOG"
else
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] ERROR: exit code $RESULT" >> "$LOG"
fi

# Verificar tamaño
du -sh "$REPO/data/" >> "$LOG" 2>&1
echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] FIN" >> "$LOG"
echo "---" >> "$LOG"
