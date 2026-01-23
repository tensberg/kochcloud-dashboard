
import os
import streamlit as st
import yaml


@st.cache_data
def load_config(path="conf/kochcloud-dashboard.yaml"):
    if not os.path.exists(path):
        print(f"Config file not found at {path}, using empty config.")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

APP_CONFIG = load_config()
