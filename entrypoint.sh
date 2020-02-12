#!/usr/bin/env bash

# Send SIGTERM to all running processes on exit
trap "/bin/kill -s TERM -1" SIGTERM SIGQUIT

case "${1}" in
    '')
        source /opt/bot/venv/bin/activate
        python -m devpotato_bot
    ;;
    *) exec "${@}" ;;
esac

