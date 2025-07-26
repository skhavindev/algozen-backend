#!/bin/bash

# Start Celery worker
cd /app/backend
celery -A backend worker --loglevel=info 