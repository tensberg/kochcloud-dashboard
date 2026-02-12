import os
import re
from attr import dataclass
import streamlit as st
from sqlalchemy.sql import text
import subprocess
import textwrap
from dashboard.config import APP_CONFIG
from dashboard.db import DB_CONNECTION as conn

WG_CONFIG = APP_CONFIG.get("wireguard", {})
WG_INTERFACE_NAME = os.environ.get("WG_INTERFACE_NAME", WG_CONFIG.get("interface_name", "wg0"))
WG_SERVER_CONFIG_FILE = os.environ.get("WG_SERVER_CONFIG_FILE", WG_CONFIG.get("server_config_file", "/etc/wireguard/wg0.conf"))
WG_SERVER_PUBLIC_KEY = os.environ.get("WG_SERVER_PUBLIC_KEY", WG_CONFIG.get("server_public_key", "UNSET_PUBLIC_KEY"))
WG_SERVER_DOMAIN = os.environ.get("WG_SERVER_DOMAIN", WG_CONFIG.get("server_domain", "vpn.webko.ch"))
WG_SERVER_PORT = os.environ.get("WG_SERVER_PORT", WG_CONFIG.get("server_port", "51820"))
WG_CLIENT_CONFIG_DOWNLOAD_FILENAME = os.environ.get("WG_CLIENT_CONFIG_DOWNLOAD_FILENAME", WG_CONFIG.get("client_config_download_filename", "Kochcloud VPN.conf"))
WG_SUBNET = os.environ.get("WG_SUBNET", WG_CONFIG.get("subnet", "10.100.1"))
WG_KOCHCLOUD_IP_ADDRESS = os.environ.get("WG_KOCHCLOUD_IP_ADDRESS", WG_CONFIG.get("kochcloud_ip_address", "10.100.0.1"))

WG = "/usr/bin/wg"
WG_QUICK = "/usr/bin/wg-quick"

WG_SERVER_IP = WG_SUBNET + ".1"

@dataclass(eq=True, frozen=True)
class WireGuardConfig:
    id: int
    created: float
    description: str
    ip_octet: int
    private_key: str
    public_key: str
    psk: str

def wg_get_vpn_configs_for_user(user_sub):
    """Get the available vpn config files for the current user"""
    configs = conn.query("""
                SELECT c.id, c.created, c.description, c.ip_octet, c.private_key, c.public_key, c.psk
                     FROM "wireguard_client" c,"user" u
                    WHERE c.user_id=u.id AND u.sub=:sub
                ORDER BY c.created
                """, ttl=0, params = { "sub": user_sub})

    wg_configs = []
    for config in configs.itertuples():
        wg_configs.append(WireGuardConfig(
            id=config.id,
            created=config.created.timestamp(),
            description=config.description,
            ip_octet=config.ip_octet,
            private_key=config.private_key,
            public_key=config.public_key,
            psk=config.psk
            ))
    return wg_configs

def wg_create_vpn_config_for_user(user_sub, description):
    """Call the external script to create a new config file for the user"""
    # check that user_sub and label are valid
    if not re.match(r"^[a-zA-Z0-9-]{1,50}$", user_sub):
        raise ValueError("Invalid user_sub")
    if not re.match(r"^[a-zA-ZäöüÄÖÜß0-9-_. ]{1,50}$", description):
        raise ValueError("Invalid description")

    # generate client keys
    client_private_key = wg_exec("genkey")
    client_public_key = wg_exec("pubkey", input=client_private_key)
    client_psk = wg_exec("genpsk")

    # insert client configuration into database, get assigned IP octet
    with conn.session as session:
        result = session.execute(text("""
                    INSERT INTO "wireguard_client" (user_id, description, private_key, public_key, psk) 
                    VALUES ((SELECT id FROM "user" WHERE sub=:sub), :description, :private_key, :public_key, :psk)
                    RETURNING ip_octet
                    """), params={
                        "sub": user_sub,
                        "description": description,
                        "private_key": client_private_key,
                        "public_key": client_public_key,
                        "psk": client_psk
                    })
        client_ip_octet = result.one()[0]
        session.commit()

    client_ip = f"{WG_SUBNET}.{client_ip_octet}"
    # add client to server configuration
    with open(WG_SERVER_CONFIG_FILE, "a") as f:
        f.write(textwrap.dedent(f"""
                # {client_ip_octet}
                # user: {user_sub}
                # description: {description}
                [Peer]
                PublicKey = {client_public_key}
                PresharedKey = {client_psk}
                AllowedIPs = {client_ip}/32
                """))

    print(f"Added new client for {user_sub} with label {description} and IP {client_ip} to {WG_INTERFACE_NAME} server configuration")

    reload_server_configuration()

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

def wg_config_file_body(config: WireGuardConfig):
    return textwrap.dedent(f"""
                # label: {config.description}

                [Interface]
                Address = {WG_SUBNET}.{config.ip_octet}/32
                DNS = {WG_KOCHCLOUD_IP_ADDRESS}
                PrivateKey = {config.private_key}

                [Peer]
                PublicKey = {WG_SERVER_PUBLIC_KEY}
                PresharedKey = {config.psk}
                Endpoint = {WG_SERVER_DOMAIN}:{WG_SERVER_PORT}
                AllowedIPs = {WG_SERVER_IP}/32,{WG_KOCHCLOUD_IP_ADDRESS}/32
                PersistentKeepalive = 25
                """)
