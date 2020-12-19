#!/usr/bin/env bash

# Send SIGTERM to all running processes on exit
trap "/bin/kill -s TERM -1" SIGTERM SIGQUIT

# Disable virtualenv check
# shellcheck disable=SC1091
source /opt/bot/venv/bin/activate

case "${1}" in
    '')
        sleep "${WAIT_BEFORE_START:-0}" # Wait for init-container to finish
        python -m devpotato_bot
    ;;
    'init_db')
        python -m devpotato_bot.init_db
    ;;
    'migrate_db')
        alembic -c /opt/bot/alembic.ini upgrade head
    ;;
    *) exec "${@}" ;;
esac

