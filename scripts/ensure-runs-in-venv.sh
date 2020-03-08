#!/usr/bin/env bash

command="$1"
# To be sure $@ will only contain the parameters of the command, not the command itself.
shift

# If we are already in a venv, run directly.
if [[ -v VIRTUAL_ENV ]]; then
    echo "Already in venv"
    ${command} "$@"

    exit $?
else
    # Load bashrc to be sure PATH is correctly set. We can't do this before this it could mess up with the enabled venv.
    source ~/.bashrc || echo "Bash RC file not found"
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
