#!/bin/bash

if [ "$ENV" = "production" ]; then
    echo "Starting in production mode..."
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
else
    echo "Starting in development mode..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi