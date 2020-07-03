# build with --squash flag, needs "experimental": true to be set in daemon.json
#
FROM python:3-alpine AS builder

COPY . /opt/bot

WORKDIR /opt/bot

RUN apk upgrade --no-cache
RUN apk add --no-cache build-base openssl openssl-dev libffi libffi-dev sqlite
RUN python -m venv venv \
 && . ./venv/bin/activate \
 && pip install -r requirements.txt \
 && pip install -e .

# ===

FROM python:3-alpine

RUN apk upgrade --no-cache
RUN apk add --no-cache bash openssl libffi fortune sqlite
RUN adduser potato --disabled-password \
                   --shell /bin/false \
                   --home /opt/bot \
                   --no-create-home

WORKDIR /opt/bot

COPY --from=builder /opt/bot/entrypoint.sh .
COPY --from=builder /opt/bot/devpotato_bot devpotato_bot
COPY --from=builder /opt/bot/alembic.ini .
COPY --from=builder /opt/bot/alembic alembic
COPY --from=builder /opt/bot/init_db.py .
COPY --from=builder /opt/bot/venv venv
COPY --from=builder /opt/bot/LICENSE .

USER potato

ENTRYPOINT ["/opt/bot/entrypoint.sh"]

