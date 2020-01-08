FROM python:3-alpine AS builder

COPY . /opt/bot

WORKDIR /opt/bot

RUN apk upgrade --no-cache \
 && apk add --no-cache alpine-sdk \
                       openssl openssl-dev \
                       libffi libffi-dev \
 && python -m venv venv \
 && . ./venv/bin/activate \
 && pip install -r requirements.txt

# ===

FROM python:3-alpine

RUN apk upgrade --no-cache \
 && apk add --no-cache bash openssl libffi fortune \
 && adduser potato --disabled-password \
                   --shell /bin/false \
                   --home /opt/bot \
                   --no-create-home

WORKDIR /opt/bot

COPY --from=builder /opt/bot/entrypoint.sh .
COPY --from=builder /opt/bot/bot.py .
COPY --from=builder /opt/bot/dice_parser.py .
COPY --from=builder /opt/bot/venv venv
COPY --from=builder /opt/bot/LICENSE .

USER potato

ENTRYPOINT ["/opt/bot/entrypoint.sh"]

