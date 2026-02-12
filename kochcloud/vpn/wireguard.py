import os
import re
import textwrap
from attr import dataclass
import streamlit as st
from dashboard.config import APP_CONFIG
import subprocess

WG_CONFIG = APP_CONFIG.get("wireguard", {})
WG_INTERFACE_NAME = os.environ.get("WG_INTERFACE_NAME", WG_CONFIG.get("interface_name", "wg0"))
WG_SERVER_CONFIG_FILE = os.environ.get("WG_SERVER_CONFIG_FILE", WG_CONFIG.get("server_config_file", "/etc/wireguard/wg0.conf"))
WG_SERVER_PUBLIC_KEY = os.environ.get("WG_SERVER_PUBLIC_KEY", WG_CONFIG.get("server_public_key", "UNSET_PUBLIC_KEY"))
WG_SERVER_DOMAIN = os.environ.get("WG_SERVER_DOMAIN", WG_CONFIG.get("server_domain", "vpn.webko.ch"))
WG_SERVER_PORT = os.environ.get("WG_SERVER_PORT", WG_CONFIG.get("server_port", "51820"))
WG_CLIENT_CONFIG_DIR = os.environ.get("WG_CLIENT_CONFIG_DIR", WG_CONFIG.get("client_config_dir", "/etc/wireguard/clients"))
WG_CLIENT_CONFIG_DOWNLOAD_FILENAME = os.environ.get("WG_CLIENT_CONFIG_DOWNLOAD_FILENAME", WG_CONFIG.get("client_config_download_filename", "Kochcloud VPN.conf"))
WG_SUBNET = os.environ.get("WG_SUBNET", WG_CONFIG.get("subnet", "10.100.1"))
WG_KOCHCLOUD_IP_ADDRESS = os.environ.get("WG_KOCHCLOUD_IP_ADDRESS", WG_CONFIG.get("kochcloud_ip_address", "10.100.0.1"))

WG = "/usr/bin/wg"
WG_QUICK = "/usr/bin/wg-quick"

WG_SERVER_IP = WG_SUBNET + ".1"

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
    if not re.match(r"^[a-zA-ZäöüÄÖÜß0-9-_. ]{1,50}$", label):
        raise ValueError("Invalid label")

    # generate client keys
    client_private_key = wg_exec("genkey")
    client_public_key = wg_exec("pubkey", input=client_private_key)
    client_psk = wg_exec("genpsk")

    # determine client IP address
    next_ip = get_next_available_ip()
    client_ip = f"{WG_SUBNET}.{next_ip}"

    # add client to server configuration
    with open(WG_SERVER_CONFIG_FILE, "a") as f:
        f.write(textwrap.dedent(f"""
                # {next_ip}
                # user: {user_sub}
                # label: {label}
                [Peer]
                PublicKey = {client_public_key}
                PresharedKey = {client_psk}
                AllowedIPs = {client_ip}/32
                """))
    
    # create client configuration file
    client_file = os.path.join(WG_CLIENT_CONFIG_DIR, f"{next_ip}-{user_sub}.conf")
    with open(client_file, "w", opener=client_config_opener) as f:
        f.write(textwrap.dedent(f"""
                # user: {user_sub}
                # label: {label}

                [Interface]
                Address = {client_ip}/32
                DNS = {WG_KOCHCLOUD_IP_ADDRESS}
                PrivateKey = {client_private_key}

                [Peer]
                PublicKey = {WG_SERVER_PUBLIC_KEY}
                PresharedKey = {client_psk}
                Endpoint = {WG_SERVER_DOMAIN}:{WG_SERVER_PORT}
                AllowedIPs = {WG_SERVER_IP}/32,{WG_KOCHCLOUD_IP_ADDRESS}/32
                PersistentKeepalive = 25
                """))

    print(f"Added new client for {user_sub} with label {label} and IP {client_ip} to {WG_INTERFACE_NAME} server configuration")

    reload_server_configuration()

    return wg_get_vpn_configs_for_user(user_sub)

def client_config_opener(path, flags):
    return os.open(path, flags, mode=0o660)

def wg_exec(command, args=[], input=None):
    """Execute a wg command with the given arguments and return the output"""
    result = subprocess.run([WG, command] + args, check=True, capture_output=True, text=True, input=input)
    return result.stdout.strip()

def reload_server_configuration():
    """Reload the WireGuard server configuration"""
    wg_quick = subprocess.Popen([WG_QUICK, "strip", WG_INTERFACE_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wg_syncconf = subprocess.Popen([WG, "syncconf", WG_INTERFACE_NAME], stdin=wg_quick.stdin, text=True)
    output, error = wg_syncconf.communicate()
    print(f"Reloaded WireGuard server configuration: {output} {error}")

def get_next_available_ip():
    """Get the next available IP address for a new client config"""
    # the last octet of the IP address is the first part of the filename before the -
    last_ip = 1
    for filename in os.listdir(WG_CLIENT_CONFIG_DIR):
        match = re.match(r"^(\d+)-.+\.conf$", filename)
        if match:
            ip = int(match.group(1))
            if ip > last_ip:
                last_ip = ip
    if last_ip >= 254:
        raise ValueError("No more available IP addresses")
    return last_ip + 1

@st.cache_data
def wg_load_config_content(filename):
    with open(os.path.join(WG_CLIENT_CONFIG_DIR, filename), "r") as f:
        return f.read()
