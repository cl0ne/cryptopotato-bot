FROM python:3-alpine AS builder

COPY . /bot

WORKDIR /bot

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
 && apk add --no-cache bash openssl libffi \
 && adduser potato --disabled-password \
	               --shell /bin/false \
				   --home /bot \
				   --no-create-home

WORKDIR /bot

COPY --from=builder /bot/entrypoint.sh .
COPY --from=builder /bot/bot.py .
COPY --from=builder /bot/venv venv
COPY --from=builder /bot/LICENSE .

USER potato

ENTRYPOINT ["/bot/entrypoint.sh"]

