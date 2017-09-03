#!/usr/bin/env bash
#
# Common implementations
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

fatal() {
    local MSG="$1"
    echo
    echo -e "${COLOR_RED}${COLOR_BOLD}Error:${COLOR_RESET} ${COLOR_YELLOW}${MSG}${COLOR_RESET}"
    echo
    exit 2
}

