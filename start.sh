#!/bin/bash

cd "$(dirname "$0")"

source env/bin/activate

uvicorn backend:app --host=0.0.0.0 --workers=3