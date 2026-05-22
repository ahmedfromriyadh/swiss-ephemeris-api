#!/bin/bash
echo "✅ Starting Swiss Ephemeris API with built-in MOSEPH ephemeris"
uvicorn app:app --host 0.0.0.0 --port $PORT
