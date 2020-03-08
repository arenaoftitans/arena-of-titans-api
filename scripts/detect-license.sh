#!/usr/bin/env bash

files_missing_license=()
for filename in "$@"; do
    if ! grep --quiet 'Copyright (C)' "${filename}"; then
        files_missing_license+=("${filename}")
    fi
done

if [[ "${#files_missing_license[@]}" -gt 0 ]]; then
    echo "Files " "${files_missing_license[@]}" "are missing a license." >&2
    exit 1
fi
