FROM python:3.13-slim@sha256:51e1a0a317fdb6e170dc791bbeae63fac5272c82f43958ef74a34e170c6f8b18

LABEL org.opencontainers.image.source=https://github.com/tensberg/kochcloud-dashboard
LABEL org.opencontainers.image.description="Dashboard application for the Kochcloud, a self-hosted cloud service."
LABEL org.opencontainers.image.licenses=MIT

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser \
    && mkdir /app && chown appuser /app

ENV PATH=/home/appuser/.local/bin:$PATH

RUN apt-get update && apt-get install -y \
    gettext-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY docker/docker-entrypoint.sh .
COPY docker/conf/ conf
COPY alembic/ alembic
COPY kochcloud-dashboard/ kochcloud-dashboard

EXPOSE 8501

ENTRYPOINT ["/app/docker-entrypoint.sh"]
