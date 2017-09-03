#!/usr/bin/env bash

# This run command is intended for local development in prod mode

PYTHONPATH=$PYTHONPATH:. \
MONGO_URI='mongodb://localhost:27017/' \
gunicorn \
    --logger-class src.common.logging.GunicornLogger \
    'app.app:run()'

