#!/usr/bin/env bash

# Don't allow undefined variables.
set -u
# Exit on error
set -e
# Exit on error in pipes
set -o pipefail


# Initializing associative array so they can be filled in user configuration
declare -A API_HOSTS
declare -A DEPLOY_API_BRANCHES
declare -A DEPLOY_BASE_DIRS
declare -A DEPLOY_HOSTS
declare -A DEPLOY_USERS

# Defined variables that can change per user before loading the user configuration
REDIS_CONF_DIR="/etc/redis.d"
REDIS_USER="redis"
REDIS_SOCKET_DIR="/var/run/redis"
# We will append type and version to it.
REDIS_WORKING_DIR="/var/lib/redis"
UWSGI_USER="uwsgi"
UWSGI_GROUP="uwsgi"
UWSGI_DEPLOY_FOLDER="/etc/uwsgi.d"
UWSGI_SOCKET_FOLDER="/var/run/uwsgi"
FRONT_LOCATION="../arena-of-titans"

# Load user configuration
source ./scripts/cli-conf.sh 2> /dev/null || echo "No user configuration file for deploy found. Testing will not be available." >&2

# Values that don't change neither per user nor per type
API_GIT_URL="https://bitbucket.org/arenaoftitans/arena-of-titans-api.git"
API_RETRIES_TIME=1
INTLJS_POLYFILL="node_modules/intl/dist/Intl.js"
MAX_API_RETRIES=5

# Global variables whose value is set in main.
API_HOST=''
DEPLOY_API_BRANCH=''
DEPLOY_HOST=''
DEPLOY_USER=''

# Set production and staging values for variables that changes per user and per type
API_HOSTS["prod"]="https://api.arenaoftitans.com"
API_HOSTS["staging"]="https://devapi.arenaoftitans.com"
DEPLOY_API_BRANCHES["prod"]="master"
# Always use current branch for staging deploy
DEPLOY_API_BRANCHES["staging"]=$(git rev-parse --abbrev-ref HEAD)
DEPLOY_BASE_DIRS["prod"]="/home/aot"
DEPLOY_BASE_DIRS["staging"]="/home/aot"
DEPLOY_USERS["prod"]="aot"
DEPLOY_USERS["staging"]="aot"
DEPLOY_HOSTS["prod"]="arenaoftitans.com"
DEPLOY_HOSTS["staging"]="arenaoftitans.com"


# Load tasks files
source scripts/deploy.sh
source scripts/collect.sh


usage() {
    echo "Deploy script for arena of titans. Usage:

$0 CMD TYPE

- CMD: deploy, collect
- TYPE: prod, staging, testing"
}


execute-on-server() {
    local commands="$1"

    # If xtrace is enabled locally, we pass it to the server
    if shopt -qo xtrace; then
        commands="set -x; $commands"
    fi

    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "${commands}"
}


exit-if-git-unclean() {
    local git_status_output=$(git status --porcelain)
    if [[ -n "${git_status_output}" ]]; then
        echo "Uncommited changes in $(pwd). Exiting" >&2
        exit 1
    fi
}


main() {
    if [[ "$#" != 2 ]]; then
        echo "Invalid number of arguments." >&2
        usage
        exit 1
    fi

    local cmd="$1"
    local type="$2"
    local version="$(date +"%s")"

    case "${type}" in
        'prod'|'staging'|'testing')
            if [[ "${type}" == "testing" ]] && [[ -z "${API_HOSTS['testing']:-}" ]]; then
                echo "Testing is not available. Exiting" >&2
                exit 1
            fi

            API_HOST="${API_HOSTS[${type}]}"
            DEPLOY_API_BRANCH="${DEPLOY_API_BRANCHES[${type}]}"
            DEPLOY_BASE_DIR="${DEPLOY_BASE_DIRS[${type}]}"
            DEPLOY_HOST="${DEPLOY_HOSTS[${type}]}"
            DEPLOY_USER="${DEPLOY_USERS[${type}]}"

            case "${cmd}" in
                'deploy')
                    deploy "${type}" "${version}";;
                'collect')
                    collect "${type}";;
                *)
                    usage
                    exit 1;;
            esac;;
        'dev')
            echo 'Cannot deploy for dev' >&2
            exit 1;;
        *)
            usage
            exit 1;;
    esac
}

main "$@"

