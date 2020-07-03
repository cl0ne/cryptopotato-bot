#!/usr/bin/env bash

# Send SIGTERM to all running processes on exit
trap "/bin/kill -s TERM -1" SIGTERM SIGQUIT

case "${1}" in
    '')
        sleep "${WAIT_BEFORE_START:-0}" # Wait for init-container to finish
        source /opt/bot/venv/bin/activate
        python -m devpotato_bot
    ;;
    'init_db')
        source /opt/bot/venv/bin/activate
        python /opt/bot/init_db.py
    ;;
    'migrate_db')
        source /opt/bot/venv/bin/activate
        alembic -c /opt/bot/alembic.ini upgrade head
    ;;
    *) exec "${@}" ;;
esac

