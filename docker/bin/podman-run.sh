#!/usr/bin/env bash
podman run -it --rm -p 8501:8501 \
    -v ~/Projekte/kochcloud-dashboard/conf/kochcloud-dashboard.yaml:/app/conf/kochcloud-dashboard.yaml \
    --env STREAMLIT_LOGGER_LEVEL=debug \
    --env-file=docker/local.env \
    --add-host=login.staging.webko.ch:host-gateway \
    ghcr.io/tensberg/kochcloud-dashboard:latest
