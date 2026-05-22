#!/bin/bash

# No download needed - using built-in ephemeris
echo "✓ Starting with built-in Swiss Ephemeris data"

# Start the application
uvicorn app:app --host 0.0.0.0 --port $PORT
