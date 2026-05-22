#!/bin/bash
echo "✅ Starting Swiss Ephemeris API (built-in ephemeris)"
uvicorn app:app --host 0.0.0.0 --port $PORT
