#!/bin/bash

PROJECT_ROOT="$(realpath $(dirname "$0"))"
export SCRIPT_FILENAME="${PROJECT_ROOT}/api.sh"
export HTML_DIRECTORY="${PROJECT_ROOT}/html"
export FCGI_SOCKET="$PROJECT_ROOT/fcgiwrap.socket"

export MIME_TYPES_PATH="/opt/homebrew/etc/nginx/mime.types"
export FASTCGI_PARAMS_PATH="/opt/homebrew/etc/nginx/fastcgi_params"
export LOG_FORMAT='[$time_iso8601] "$request" $status ${body_bytes_sent}B Upstream:$upstream_response_time'

TEMP_CONF="$(mktemp)"
# Ensure that the temporary file is deleted when the script exits
cleanup() {
    echo "Cleaning up..."
    kill $FCGIWRAP_PID
    rm "$FCGI_SOCKET"
    rm -f "$TEMP_CONF"
}
trap cleanup EXIT
# Use envsubst to substitute the environment variables and create the temporary nginx configuration file
DEV_CONF="${PROJECT_ROOT}/dev.conf" 
envsubst < "$DEV_CONF" > "$TEMP_CONF"
fcgiwrap -s "unix:$FCGI_SOCKET" &
FCGIWRAP_PID=$!
# cat "$TEMP_CONF"
nginx -g 'daemon off;' -c "$TEMP_CONF"
