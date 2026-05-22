#!/bin/bash

echo " Starting Swiss Ephemeris API..."

# Download ephemeris files
python download_ephe.py

# Start the server
uvicorn app:app --host 0.0.0.0 --port $PORT
