#!/usr/bin/env bash
#
# lint the project, omitting reports, just fail on any error.
#
# From pl-cloud-starter/backend/cloud-starter-falcon::
#
#   ./build/lint.sh
#
lint() {
    local PROJECT="$1"
    local OUTPUT

    OUTPUT=$(pylint -f parseable --errors-only --jobs 4 ${PROJECT})

    if [ $? -ne 0 ]; then
        echo
        echo -e "$OUTPUT"
        echo
        echo "Pylint returned a fatal error - see above."
        exit 2
    else
        echo "pylint ${PROJECT} complete"
    fi
}

lint app
lint test