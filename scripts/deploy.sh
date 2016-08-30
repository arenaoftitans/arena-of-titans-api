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
declare -A DEPLOY_HOSTS
declare -A DEPLOY_USERS

# Defined variables that can change per user before loading the user configuration
UWSGI_USER="uwsgi"
UWSGI_GROUP="uwsgi"
UWSGI_DEPLOY_FOLDER="/etc/uwsgi.d"
UWSGI_SOCKET_FOLDER="/var/run/uwsgi"
DEPLOY_BASE_DIR="~"
FRONT_LOCATION="../arena-of-titans"

# Load user configuration
source ./scripts/deploy-conf.sh 2> /dev/null || echo "No user configuration file for deploy found. Testing will not be available." >&2

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
DEPLOY_USERS["prod"]="aot"
DEPLOY_USERS["staging"]="aot"
DEPLOY_HOSTS["prod"]="arenaoftitans.com"
DEPLOY_HOSTS["staging"]="arenaoftitans.com"


usage() {
    echo "Deploy script for arena of titans. Usage:

$0 TYPE"
}


deploy() {
    local type="$1"
    local version="$2"

    echo "Deploying frontend"
    deploy-front "${type}" "${version}"
    echo "Deploying API"
    deploy-api "${type}" "${version}"

    # Make deployed version lastest version
    echo "Updating default version"
    execute-on-server "ln --force --no-dereference --symbolic ${DEPLOY_BASE_DIR}/${type}/front/${version} ${DEPLOY_BASE_DIR}/${type}/front/latest"
    execute-on-server "ln --force --no-dereference --symbolic ${DEPLOY_BASE_DIR}/${type}/api/${version} ${DEPLOY_BASE_DIR}/${type}/api/latest"
    execute-on-server "sudo ln -sf ${UWSGI_SOCKET_FOLDER}/aot-api-ws-${type}-${version}.sock ${UWSGI_SOCKET_FOLDER}/aot-api-ws-${type}-latest.sock"
    echo "Deploying is done"
}


deploy-front() {
    local type="$1"
    local version="$2"
    local front_dir="${DEPLOY_BASE_DIR}/${type}/front/${version}"

    execute-on-server "mkdir -p ${front_dir}"
    pushd "${FRONT_LOCATION}" > /dev/null
        release "${type}" "${version}"
        echo -e "\tBuilding frontend"
        npm run clean > /dev/null
        npm run config -- --type "${type}" --version "${version}" > /dev/null
        npm run prodbuild > /dev/null

        echo -e "\tPushing code to server"
        # Correct load path so scripts are loaded from the correct version.
        sed -Ei "s#\"(/dist/[a-z\-]+bundle.js)\"#\"/${version}\1\"#g" index.html
        sed -Ei "s#\"(/dist/[a-z\-]+bundle)\"#\"/${version}\1\"#g" dist/vendor-bundle.js
        # Correct assets path in index
        sed -Ei "s#\"(/assets/.*)\"#\"/${version}\1\"#g" index.html
        # Correct assets path in included HTML
        sed -Ei "s#\"(/assets/[^\"]*)\"#\"/${version}\1\"#g" dist/*.js
        # Correct assets path in included CSS
        sed -Ei "s#url\((/assets/[^\)]*)\)#url(/${version}\1)#g" dist/*.js

        # Sync with server
        rsync -a --delete --info=progress2 --exclude="*.map" "index.html" "assets" "dist" "${DEPLOY_USER}@${DEPLOY_HOST}:${front_dir}"
        scp "${INTLJS_POLYFILL}" "${DEPLOY_USER}@${DEPLOY_HOST}:${front_dir}"
    popd > /dev/null
}


release() {
    local type="$1"
    local version="$2"

    echo -e "\tReleasing"

    git push -q

    if [[ "${type}" == "prod" ]]; then
        git tag "${version}"
        git push --tags
    fi
}


deploy-api() {
    local type="$1"
    local version="$2"
    local cfg_file

    if [[ "${type}" == 'prod' ]]; then
        exit-if-git-unclean
    fi
    release "${type}" "${version}"

    if [[ "${type}" == "testing" ]]; then
        cfg_file="/tmp/config.testing.toml-${version}"
        scp "config/config.testing.toml" "${DEPLOY_USER}@${DEPLOY_HOST}:/tmp/config.testing.toml-${version}"
    fi

    execute-on-server "set -u && \
        set -e && \
        $(declare -f deploy-api-server) && \
        $(declare -f wait-api-to-start) && \
        export API_GIT_URL=\"${API_GIT_URL}\" && \
        export API_HOST=\"${API_HOST}\" && \
        export API_RETRIES_TIME=\"${API_RETRIES_TIME}\" && \
        export DEPLOY_API_BRANCH=\"${DEPLOY_API_BRANCH}\" && \
        export MAX_API_RETRIES=\"${MAX_API_RETRIES}\" && \
        export UWSGI_DEPLOY_FOLDER=\"${UWSGI_DEPLOY_FOLDER}\" && \
        export UWSGI_GROUP=\"${UWSGI_GROUP}\" && \
        export UWSGI_USER=\"${UWSGI_USER}\" && \
        deploy-api-server ${type} ${version} ${cfg_file:-}"
}


deploy-api-server() {
    local type="$1"
    local version="$2"
    local cfg_file="${3:-}"
    local api_dir="${type}/api/${version}"
    local uwsgi_file="uwsgi.ini"
    local log_file="api.log"

    mkdir -p "${api_dir}"
    pushd "${api_dir}" > /dev/null
        echo -e "\tCloning API from ${API_GIT_URL} to track branch ${DEPLOY_API_BRANCH}"
        git clone -q "${API_GIT_URL}" .
        git checkout -q "${DEPLOY_API_BRANCH}" > /dev/null

        echo -e "\tBuilding configuration"
        if [[ -n "${cfg_file:-}" ]] && [[ -f "${cfg_file:-}" ]]; then
            mv "${cfg_file}" config/config.testing.toml
        fi

        make config type=testing version="${version}"
        make static type=testing version="${version}"
        uwsgi_file="$(pwd)/${uwsgi_file}"
        chmod 660 "${uwsgi_file}"
        sudo chown "${UWSGI_USER}:${UWSGI_GROUP}" "${uwsgi_file}"
        sudo ln -s "${uwsgi_file}" "${UWSGI_DEPLOY_FOLDER}/aot-api-${version}.ini"

        echo > "${log_file}"
        chown "$(whoami):${UWSGI_GROUP}" "${log_file}"
        chmod 660 "${log_file}"
    popd > /dev/null

    echo -e "\tWaiting for API to start"
    wait-api-to-start "${type}" "${version}"
}


wait-api-to-start() {
    local type="$1"
    local version="$2"
    local retries=0

    while ! curl -f "${API_HOST}/ws/${version}" > /dev/null 2>&1 && [[ "${retries}" < "${MAX_API_RETRIES}" ]]; do
        sleep "${API_RETRIES_TIME}"
        # Maths operation returns their value, which means ((retries++)) will return with non zero
        # status code and so exit the script.
        ((retries++)) || true
    done

    if [[ "${retries}" == "${MAX_API_RETRIES}" ]]; then
        echo "Api could not start. Exiting" >&2
        exit 1
    fi
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
    if [[ "$#" != 1 ]]; then
        echo "Invalid number of arguments." >&2
        usage
        exit 1
    fi

    local type="$1"
    local version="$(date +"%s")"

    case "${type}" in
        'prod'|'staging'|'testing')
            if [[ "${type}" == "testing" ]] && [[ -z "${API_HOSTS['testing']:-}" ]]; then
                echo "Testing is not available. Exiting" >&2
                exit 1
            fi

            API_HOST="${API_HOSTS[${type}]}"
            DEPLOY_API_BRANCH="${DEPLOY_API_BRANCHES[${type}]}"
            DEPLOY_HOST="${DEPLOY_HOSTS[${type}]}"
            DEPLOY_USER="${DEPLOY_USERS[${type}]}"

            deploy "${type}" "${version}";;
        'dev')
            echo 'Cannot deploy for dev' >&2
            exit 1;;
        *)
            usage
            exit 1;;
    esac
}

main "$@"

