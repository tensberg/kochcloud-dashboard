FROM python:3.13-slim

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser \
    && mkdir /app && chown appuser /app

ENV PATH=/home/appuser/.local/bin:$PATH

RUN apt-get update && apt-get install -y \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r /app/requirements.txt

COPY docker/docker-entrypoint.sh .
COPY docker/conf/ conf
COPY alembic/ alembic
COPY kochcloud-dashboard/ kochcloud-dashboard

EXPOSE 8501

ENTRYPOINT ["/app/docker-entrypoint.sh"]
