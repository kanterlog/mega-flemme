#!/bin/bash
# Script pour tuer le processus sur le port 3010 et lancer Next.js automatiquement
PORT=3010
PID=$(fuser -n tcp $PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
  echo "Killing process on port $PORT (PID: $PID)"
  kill -9 $PID
fi
cd sylvie-v3 && npm run dev
