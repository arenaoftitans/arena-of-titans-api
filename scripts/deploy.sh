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
    echo "Deploy is done"
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
        npm run buildprod > /dev/null

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

        # Reset index.html
        git checkout index.html
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
        export DEPLOY_BASE_DIR=\"${DEPLOY_BASE_DIR}\" && \
        export MAX_API_RETRIES=\"${MAX_API_RETRIES}\" && \
        export REDIS_CONF_DIR=\"${REDIS_CONF_DIR}\" && \
        export REDIS_USER=\"${REDIS_USER}\" && \
        export REDIS_WORKING_DIR=\"${REDIS_WORKING_DIR}\" && \
        export UWSGI_DEPLOY_FOLDER=\"${UWSGI_DEPLOY_FOLDER}\" && \
        export UWSGI_GROUP=\"${UWSGI_GROUP}\" && \
        export UWSGI_USER=\"${UWSGI_USER}\" && \
        deploy-api-server ${type} ${version} ${cfg_file:-}"
}


deploy-api-server() {
    local type="$1"
    local version="$2"
    local cfg_file="${3:-}"
    local api_dir="${DEPLOY_BASE_DIR}/${type}/api/${version}"
    local uwsgi_file="uwsgi.ini"
    local log_file="api.log"
    local redis_cgf_file="aot-api-${type}-${version}.conf"

    mkdir -p "${api_dir}"
    pushd "${api_dir}" > /dev/null
        echo -e "\tCloning API from ${API_GIT_URL} to track branch ${DEPLOY_API_BRANCH}"
        git clone -q "${API_GIT_URL}" .
        git checkout -q "${DEPLOY_API_BRANCH}" > /dev/null

        echo -e "\tBuilding configuration"
        if [[ -n "${cfg_file:-}" ]] && [[ -f "${cfg_file:-}" ]]; then
            mv "${cfg_file}" config/config.testing.toml
        fi

        # Build config
        make config type="${type}" version="${version}"
        make static type="${type}" version="${version}"

        # Setup redis
        sudo cp "redis.conf" "${REDIS_CONF_DIR}/${redis_cgf_file}"
        sudo chown "root:${REDIS_USER}" "${REDIS_CONF_DIR}/${redis_cgf_file}"
        sudo mkdir -p "${REDIS_WORKING_DIR}/${type}-${version}/"
        sudo chown -R "${REDIS_USER}:${REDIS_USER}" "${REDIS_WORKING_DIR}/"
        sudo systemctl start "redis@${type}-${version}"
        sudo systemctl enable "redis@${type}-${version}"

        # Setup uwsgi
        uwsgi_file="$(pwd)/${uwsgi_file}"
        chmod 660 "${uwsgi_file}"
        sudo chown "${UWSGI_USER}:${UWSGI_GROUP}" "${uwsgi_file}"
        sudo ln -s "${uwsgi_file}" "${UWSGI_DEPLOY_FOLDER}/aot-api-${version}.ini"

        # Prepare log file
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

