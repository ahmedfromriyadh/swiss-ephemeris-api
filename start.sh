#!/bin/bash

# Get the current working directory
WORK_DIR=$(pwd)
EPH_DIR="${WORK_DIR}/eph"

# Download ephemeris files if they don't exist
if [ ! -d "$EPH_DIR" ] || [ -z "$(ls -A $EPH_DIR 2>/dev/null)" ]; then
    echo "Downloading Swiss Ephemeris data files to $EPH_DIR..."
    python download_ephe.py
else
    echo "✓ Ephemeris files already exist in $EPH_DIR"
fi

# Start the application
uvicorn app:app --host 0.0.0.0 --port $PORT
