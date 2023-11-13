#!/bin/bash
# Script referenced https://dylancastillo.co/fastapi-nginx-gunicorn/

NAME=fastapi-app
DIR=/home/fastapi-user/M4
USER=fastapi-user
GROUP=fastapi-user
WORKERS=3
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=$DIR/.venv/bin/activate
BIND=unix:$DIR/run/gunicorn.sock
LOG_LEVEL=error

cd $DIR
source $VENV

exec gunicorn backend:app \
  -b 0.0.0.0 \
  --name $NAME \
  --workers $WORKERS \
  --worker-class $WORKER_CLASS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=-