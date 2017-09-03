#!/usr/bin/env bash


PYTHONPATH=$PYTHONPATH:. \
gunicorn \
    -b 0.0.0.0:8000 \
    --logger-class app.common.logging.GunicornLogger \
    'src.app:run()'
