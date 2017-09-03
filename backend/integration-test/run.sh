#!/usr/bin/env bash
#
# Run an integration test on the api/datastore
#
# Return non-zero on any non-successful call of this script
#

if test -t 1; then
    if [ -n `which tput` ]; then
        # If running in a terminal, enable colors
        COLOR_BLACK="$(tput setaf 0)"
        COLOR_RED="$(tput setaf 1)"
        COLOR_GREEN="$(tput setaf 2)"
        COLOR_YELLOW="$(tput setaf 3)"
        COLOR_BLUE="$(tput setaf 4)"
        COLOR_MAGENTA="$(tput setaf 5)"
        COLOR_CYAN="$(tput setaf 6)"
        COLOR_WHITE="$(tput setaf 7)"
        COLOR_BOLD="$(tput bold)"
        COLOR_DIM="$(tput dim)"
        COLOR_RESET="$(tput sgr0)"
    fi
fi

trap '{ echo -ne "${COLOR_RESET}"; }' EXIT

show_help() {
    echo
    echo "Usage: run.sh [-hqb] [-d delay] [-t test] [-e environment] [-n count]"
    echo
    echo "Run integration tests against an environment"
    echo
    echo "Options:"
    echo "  -h, --help               Show this help message and exit."
    echo "  -q, --quiet              Display nothing on the console; rely on exit code."
    echo "  -b, --bail               Stop tests on first failure."
    echo "  -d, --delay delayMillis  Delay this many milliseconds between requests. Default = 0."
    echo "  -t, --test test          Run one of: smoke, integration, regression test. Default = smoke."
    echo "  -e, --env environment    Run against one of: local, dev, ppe, pd. Default = local."
    echo "  -n, --count iterations   Run this many iterations. Default = 1."
    echo
    echo "Examples:"
    echo "  ./run.sh                 Run the smoke test, locally, one time."
    echo "  ./run.sh -t smoke -e pd  Run the smoke test against prod, one time."
    echo
}

fatal() {
    local MSG="$1"
    echo
    echo -e "${COLOR_RED}${COLOR_BOLD}Error:${COLOR_RESET} ${COLOR_YELLOW}${MSG}${COLOR_RESET}"
    show_help
    exit 2
}

# defaults
TEST='smoke'
ENVIRONMENT='local'
ITERATIONS=1
OPTIONS='--color'
NUMBER_RE='^[0-9]+$'

VALID_TESTS=('smoke' 'regression' 'integration')
VALID_ENVS=('local' 'dev' 'ppe' 'pd')

while [[ $# -gt 0 ]]; do
    key="$1"
    case ${key} in
        -h|--help)
            show_help
            # It is an error to ask for help ;) - want all calls that don't result in a
            # successful test to return a non-zero exit code.
            exit 1
            ;;

        -q|--quiet)
            OPTIONS="${OPTIONS} --silent "
            ;;

        -b|--bail)
            OPTIONS="${OPTIONS} --bail "
            ;;

        -d|--delay)
            if [[ $2 =~ ${NUMBER_RE} ]]; then
                OPTIONS="${OPTIONS} --delay-request $2 "
            else
                fatal "Not a valid integer for -n: '$2'"
            fi
            shift # past argument
            ;;

        -t|--test)
            if [[ " ${VALID_TESTS[@]} " =~ " $2 " ]]; then
                TEST=$2
            else
                fatal "Not a valid test: '$2'"
            fi
            shift # past argument
            ;;

        -e|--env)
            if [[ " ${VALID_ENVS[@]} " =~ " $2 " ]]; then
                ENVIRONMENT=$2
            else
                fatal "Not a valid environment: '$2'"
            fi
            shift # past argument
            ;;

        -n|--count)
            if [[ $2 =~ ${NUMBER_RE} ]]; then
               ITERATIONS=$2
            else
                fatal "Not a valid integer for -n: '$2'"
            fi
            shift # past argument
            ;;

        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift # past argument or value
done

# cd to local dir for relative paths
(
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd ${SCRIPT_DIR}

    CMD="${OPTIONS} -n ${ITERATIONS} -e postman/env.${ENVIRONMENT}.json postman/test.${TEST}.json"
    echo "Running: newman run $CMD"

    newman run ${CMD}
)