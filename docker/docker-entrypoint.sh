#!/usr/bin/env bash

set -euo pipefail

APP_PID=

runProcess() {
    COMMAND_PATH=$1
    shift
    ${COMMAND_PATH} "$@" &

    APP_ID=${!}
    wait ${APP_ID}
}

stopRunningProcess() {
    # Based on https://linuxconfig.org/how-to-propagate-a-signal-to-child-processes-from-a-bash-script
    if test ! "${APP_PID}" = '' && ps -p ${APP_PID} > /dev/null ; then
       > /proc/1/fd/1 echo "Stopping ${COMMAND_PATH} which is running with process ID ${APP_PID}"

       kill -TERM ${APP_PID}
       > /proc/1/fd/1 echo "Waiting for ${COMMAND_PATH} to process SIGTERM signal"

        wait ${APP_PID}
        > /proc/1/fd/1 echo "All processes have stopped running"
    else
        > /proc/1/fd/1 echo "${COMMAND_PATH} was not started when the signal was sent or it has already been stopped"
    fi
}

cd /app

echo "# initializing configuration"

mkdir --parents /app/.streamlit

envsubst < /app/conf/alembic.ini.template > /app/alembic.ini
envsubst < /app/conf/streamlit/config.toml.template > /app/.streamlit/config.toml
envsubst < /app/conf/streamlit/secrets.toml.template > /app/.streamlit/secrets.toml

trap stopRunningProcess EXIT TERM

echo "# running alembic database schema migration"

runProcess alembic upgrade head

echo "# running streamlit app kochcloud-dashboard"

runProcess streamlit run /app/kochcloud-dashboard/kochcloud-dashboard-app.py
