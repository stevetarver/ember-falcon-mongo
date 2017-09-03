#!/usr/bin/env bash

PYTHONPATH=$PYTHONPATH:. \
gunicorn \
    -b 0.0.0.0:8000 \
    --workers 5 \
    --logger-class app.common.logging.GunicornLogger \
    'app.app:run()'
