#!/usr/bin/env bash

set -eu

function test-is-in-docker() {
    if [[ -f /proc/self/cgroup ]] && grep -q docker /proc/self/cgroup; then
        return 0
    elif [[ -f /.dockerenv ]]; then
        return 0
    fi

    return 1
}

readonly command="$1"
# To be sure $@ will only contain the parameters of the command, not the command itself.
shift

# If we are already in a venv or if the are in docker, run directly.
if [[ -v VIRTUAL_ENV || test-is-in-docker ]]; then
    echo "Already in venv"
    ${command} "$@"

    exit $?
else
    # Load bashrc to be sure PATH is correctly set. We can't do this before this it could mess up with the enabled venv.
    # We don't want to fail if the bashrc file contains unbound variables.
    set +u
    source ~/.bashrc || echo "Bash RC file not found"
    set -u
    # If not and pipenv is installed, run with pipenv.
    if command -v pipenv > /dev/null; then
        echo "Running in venv with pipenv"
        pipenv run "${command}" "$@"

        exit $?
    else
        echo "Not in an virtual env and don't know how to run in one." >&2
        exit 1
    fi
fi
