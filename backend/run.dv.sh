#!/usr/bin/env bash

# First line appends the current directory to the python path so gunicorn can
# find our logging implementation
PYTHONPATH=$PYTHONPATH:. \
LOG_MODE=LOCAL \
MONGO_URI='mongodb://localhost:27017/' \
gunicorn \
    --reload \
    --logger-class app.common.logging.GunicornLogger \
    'app.app:run()'

