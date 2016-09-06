collect() {
    local type="$1"

    execute-on-server "set -u && \
        set -e && \
        export DEPLOY_BASE_DIR=\"${DEPLOY_BASE_DIR}\" && \
        export REDIS_CONF_DIR=\"${REDIS_CONF_DIR}\" && \
        export REDIS_SOCKET_DIR=\"${REDIS_SOCKET_DIR}\" && \
        export REDIS_WORKING_DIR=\"${REDIS_WORKING_DIR}\" && \
        export UWSGI_DEPLOY_FOLDER=\"${UWSGI_DEPLOY_FOLDER}\" && \
        $(declare -f collect-on-server) && \
        $(declare -f _collect-api-on-server) && \
        $(declare -f _collect-front-on-server) && \
        collect-on-server ${type}"
}


collect-on-server() {
    local type="$1"
    local api_dir="${DEPLOY_BASE_DIR}/${type}/api"
    local front_dir="${DEPLOY_BASE_DIR}/${type}/front"
    local versions_to_collect=()
    local latest

    pushd "${front_dir}" > /dev/null
        latest=$(readlink -f latest)
        latest="${latest##*/}"
        for version in $(ls -1 | grep -v latest); do
            keys=$(redis-cli -s "${REDIS_SOCKET_DIR}/aot-api-${type}-${version}.sock" keys \*)
            if [[ -z "${keys}" && "${version}" != "${latest}" ]]; then
                versions_to_collect+=("${version}")
            fi
        done
    popd > /dev/null

    # No versions to collect
    if [[ "${#versions_to_collect[@]}" == 0 ]]; then
        echo "No version to collect." >&2
        exit 0
    fi

    _collect-front-on-server
    _collect-api-on-server

    echo "Collect is done"
}


_collect-front-on-server() {
    # versions_to_collect and front_dir must come from caller

    pushd "${front_dir}" > /dev/null
        for version in "${versions_to_collect[@]}"; do
            echo "Collecting front for ${version}"
            rm -rf "${version}"
        done
    popd > /dev/null
}


_collect-api-on-server() {
    # versions_to_collect, type and api_dir must come from caller

    pushd "${api_dir}" > /dev/null
        for version in "${versions_to_collect[@]}"; do
            echo "Collecting api for ${version}"
            echo -e "\tDisable uwsgi"
            sudo rm "${UWSGI_DEPLOY_FOLDER}/aot-api-${version}.ini"

            echo -e "\tDisable redis"
            sudo systemctl disable "redis@${type}-${version}"
            sudo systemctl stop "redis@${type}-${version}"
            sudo rm "${REDIS_CONF_DIR}/aot-api-${type}-${version}.conf"
            sudo rm -rf "${REDIS_WORKING_DIR}/${type}-${version}"

            echo -e "\tDelete API files"
            rm -rf "${version}"
        done
    popd > /dev/null
}

