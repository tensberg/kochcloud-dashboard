# About

Dashboard application for the Kochcloud, a self-hosted cloud service.
The goal is to provide an overview of all available services to logged-in users as well as self-service configuration for the users not available in the hosted services.

Built using Streamlit to keep the coding effort as simple and lightweight as possible.

# Email Passwords

The Kochcloud Dashboard currently implements generating app passwords for the [Dovecot IMAP Server](https://dovecot.org/).
Dovecot can use a [SQL passdb](https://doc.dovecot.org/2.4.2/core/config/auth/databases/sql.html) to verify user credentials.
The Kochcloud Dashboard supports this by containing an `app_token` database table which stores hashed passwords and a UI to generate new entries for a user.
Dovecot can use this table to verify passwords with the following auth configuration:

```
sql_driver = pgsql

pgsql localhost {
  parameters {
    dbname = kochcloud_dashboard
    user = kochcloud_dashboard
    password = my_db_password
  }
}

passdb sql {
  query = \
    UPDATE "app_token" t SET last_used=NOW() \
    WHERE \
      t.user_id=(SELECT id FROM "user" WHERE email='%{user}@my-domain.com') \
      AND t.app='dovecot' \
      AND hash=crypt('%{password}',hash) \
    RETURNING NULL AS password, 'Y' as nopassword
}
```

Note that currently the DB does not contain sufficient data to support `userdb` queries, so the userdb needs to be configured using a different datasource.

The Dovecot password functionality is inspired by [devicepasswords](https://github.com/varbin/devicepasswords).

# VPN Configuration

A simple interface to download WireGuard VPN configuration files for the logged-in user.
Requires that the Kochcloud Dashboard server is also the WireGuard server and that the WireGuard configuration is accessible in the container at /etc/wireguard.

WireGuard client configurations are stored in the DB.
Configurations are linked to the logged-in user.
A default configuration is created on first access of the VPN page.
The config files for these configurations can be downloaded via the UI.
When a new client is generated, the corresponding peer configuration is added to the server using the wg/wg-quick tools.

The generated configuration allows clients access to the WireGuard host under both the WireGuard interface IP and the LAN IP of the host.
This allows access to all services on the host (the Kochcloud), but not to the rest of the network.
The configuration is based on the [PiHole WireGuard instructions](https://docs.pi-hole.net/guides/vpn/wireguard/client/).

