#!/usr/bin/env bash
podman run -it --rm -p 8501:8501 \
    --name kochcloud-dashboard-localtest \
    -v ~/Projekte/kochcloud-dashboard/conf/kochcloud-dashboard.yaml:/app/conf/kochcloud-dashboard.yaml \
    -v ~/Projekte/kochcloud-dashboard/conf/wireguard/wg0.conf:/etc/wireguard/wg0.conf \
    --env STREAMLIT_LOGGER_LEVEL=debug \
    --env-file=docker/local.env \
    --add-host=login.staging.webko.ch:host-gateway \
    --cap-add=NET_ADMIN \
    ghcr.io/tensberg/kochcloud-dashboard:latest
