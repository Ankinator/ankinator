#!/usr/bin/env bash

#Currently not used, just in case we need a celery worker for api
#python -m celery --app celery_consumer worker --loglevel=INFO --detach
#gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 --log-file - --access-logfile - api.main:app