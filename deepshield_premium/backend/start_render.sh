#!/bin/bash
# Helper to run app locally with gunicorn + uvicorn worker
cd "$(dirname "$0")"
exec gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
