import os
import re
from attr import dataclass
import streamlit as st
from dashboard.config import APP_CONFIG

WG_CONFIG = APP_CONFIG.get("wireguard", {})
WG_SERVER_CONFIG_FILE = os.environ.get("WG_SERVER_CONFIG_FILE", WG_CONFIG.get("server_config_file", "/etc/wireguard/wg0.conf"))
WG_CLIENT_CONFIG_DIR = os.environ.get("WG_CLIENT_CONFIG_DIR", WG_CONFIG.get("client_config_dir", "/etc/wireguard/clients"))
WG_CLIENT_CONFIG_DOWNLOAD_FILENAME = os.environ.get("WG_CLIENT_CONFIG_DOWNLOAD_FILENAME", WG_CONFIG.get("client_config_download_filename", "Kochcloud VPN.conf"))

@dataclass(eq=True, frozen=True)
class WireGuardConfig:
    filename: str
    label: str
    created_at: float

def wg_get_vpn_configs_for_user(user_sub):
    """Get the available vpn config files for the current user"""
    configs = []
    for filename in os.listdir(WG_CLIENT_CONFIG_DIR):
        match = re.match(r"^\d+-(.+)\.conf$", filename)
        if match and match.group(1) == user_sub:
            with open(os.path.join(WG_CLIENT_CONFIG_DIR, filename), "r") as f:
                label = "Unbekannt"
                for line in f:
                    if line.startswith("# label:"):
                        label = line.split(":", 1)[1].strip()
                        break
            created_at = os.path.getctime(os.path.join(WG_CLIENT_CONFIG_DIR, filename))
            configs.append(WireGuardConfig(filename=filename, label=label, created_at=created_at))
    return configs

def wg_create_vpn_config_for_user(user_sub, label):
    """Call the external script to create a new config file for the user"""
    # check that user_sub and label are valid
    if not re.match(r"^[a-zA-Z0-9-]{1,50}$", user_sub):
        raise ValueError("Invalid user_sub")
    if not re.match(r"^[a-zA-Z0-9-_. ]{1,50}$", label):
        raise ValueError("Invalid label")
    # todo
    return wg_get_vpn_configs_for_user(user_sub)

@st.cache_data
def wg_load_config_content(filename):
    with open(os.path.join(WG_CLIENT_CONFIG_DIR, filename), "r") as f:
        return f.read()
