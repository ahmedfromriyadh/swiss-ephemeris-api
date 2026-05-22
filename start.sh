#!/bin/bash

# Download ephemeris files if they don't exist
if [ ! -d "/app/eph" ] || [ -z "$(ls -A /app/eph)" ]; then
    echo "Downloading Swiss Ephemeris data files..."
    python download_ephe.py
fi

# Start the application
uvicorn app:app --host 0.0.0.0 --port $PORT
