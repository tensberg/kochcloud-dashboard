import streamlit as st
import qrcode
import qrcode.image.svg
from vpn.wireguard import *

user_sub = st.user.sub

@st.cache_data
def create_qr_code(config_content):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(config_content, image_factory=factory)
    return img.to_string(encoding='unicode')

@st.fragment
def show_vpn_config(config: WireGuardConfig):
    config_content = wg_config_file_body(config)
    config_qr_code = create_qr_code(config_content)
    with st.container(border=True, width="content", horizontal_alignment="center"):
        with st.container(horizontal_alignment="center", width="content"):
            st.markdown(f"**{config.description}**")
        st.image(config_qr_code)
        st.download_button(":material/download: Konfiguration herunterladen", config_content, 
                        file_name=WG_CLIENT_CONFIG_DOWNLOAD_FILENAME, mime="text/plain", key=f"download_{config.id}")

# main app

st.title("Kochcloud VPN")

st.write("Mit dem Kochcloud VPN können Sie von unterwegs auf alle Dienste der Kochcloud zugreifen. Laden Sie einfach die Konfiguration auf Ihr Smartphone oder Ihren Laptop und richten Sie die Verbindung mit der WireGuard App ein.")

st.subheader("1. WireGuard App installieren")

st.link_button(label="WireGuard für Android", icon=":material/download:", url="https://play.google.com/store/apps/details?id=com.wireguard.android")

st.subheader("2. VPN Konfiguration in WireGuard App importieren")

st.write("Laden Sie die VPN Konfiguration herunter und importieren Sie sie in die WireGuard App. Öffnen Sie die App, klicken Sie auf das Plus-Symbol und wählen Sie 'Aus Datei oder Archiv importieren'. Alternativ können Sie die Konfiguration auch per QR-Code importieren.")

# show existing configs for the user
configs = wg_get_vpn_configs_for_user(user_sub)
if not configs:
    wg_create_vpn_config_for_user(user_sub, "Smartphone")
    configs = wg_get_vpn_configs_for_user(user_sub)

for config in configs:
    show_vpn_config(config)

if len(configs) < 5:
    with st.expander("VPN Konfiguration hinzufügen"):
        with st.form("create_vpn_config_form", border=False):
            label = st.text_input("Bezeichnung", value=f"Smartphone {len(configs) + 1}")
            create_button = st.form_submit_button("Erstellen", icon=":material/add:")

        if create_button:
            wg_create_vpn_config_for_user(user_sub, label)
            st.rerun()