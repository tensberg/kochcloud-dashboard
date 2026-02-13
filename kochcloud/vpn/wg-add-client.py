#!/usr/bin/env python3

# Standalone python script which to add a new client to the WireGuard server configuration.
# Called via sudo from the main application because it needs access to the WireGuard configuration file and to execute wg commands.

import sys
import re
import subprocess
import tempfile
import textwrap

WG = "/usr/bin/wg"
WG_QUICK = "/usr/bin/wg-quick"

def usage():
    print("Usage: {} <wg_interface_name> <user> <description> <client_ip> <client_public_key> <client_psk>".format(sys.argv[0]))
    sys.exit(1)

def validate_args(wg_interface_name, user, description, client_ip, client_public_key, client_psk):
    if not re.match(r'^[a-zA-Z0-9_-]{1,10}$', wg_interface_name):
        print("Error: wg_interface_name contains invalid characters.")
        sys.exit(1)
    if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', user):
        print("Error: user contains invalid characters.")
        sys.exit(1)
    if not re.match(r'^[a-zA-ZäöüÄÖÜß0-9 _-]{1,50}$', description):
        print("Error: description contains invalid characters.")
        sys.exit(1)
    if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', client_ip):
        print("Error: client_ip is not a valid IPv4 address.")
        sys.exit(1)
    if not re.match(r'^[A-Za-z0-9+/=]{44}$', client_public_key):
        print("Error: client_public_key is not a valid base64 string.")
        sys.exit(1)
    if not re.match(r'^[A-Za-z0-9+/=]{44}$', client_psk):
        print("Error: client_psk is not a valid base64 string.")
        sys.exit(1)

def wg_add_client(wg_interface_name, user, description, client_ip, client_public_key, client_psk):
    validate_args(wg_interface_name, user, description, client_ip, client_public_key, client_psk)

    config_path = f"/etc/wireguard/{wg_interface_name}.conf"
    # Append client to server configuration
    try:
        with open(config_path, 'a') as f:
            f.write(textwrap.dedent(f"""
                    # user: {user}
                    # description: {description}
                    [Peer]
                    PublicKey = {client_public_key}
                    PresharedKey = {client_psk}
                    AllowedIPs = {client_ip}/32

                    """))
    except Exception as e:
        print(f"Error writing to {config_path}: {e}")
        sys.exit(1)

    print(f"Client {description} for {user} added with IP {client_ip} to WireGuard configuration {wg_interface_name}.")

    # Apply new configuration
    # call out to bash to use process substitution for wg-quick strip, because wg syncconf doesn't support reading from stdin
    cmd = f"{WG} syncconf {wg_interface_name} <({WG_QUICK} strip {wg_interface_name})"
    result = subprocess.run(cmd, shell=True, executable="/bin/bash")
    if result.returncode != 0:
        print("WARNING: Failed to apply new WireGuard configuration. Please sync the configuration manually.")

def main():
    if len(sys.argv) != 7:
        usage()
    wg_interface_name, user, description, client_ip, client_public_key, client_psk = sys.argv[1:7]
    wg_add_client(wg_interface_name, user, description, client_ip, client_public_key, client_psk)

if __name__ == "__main__":
    main()
