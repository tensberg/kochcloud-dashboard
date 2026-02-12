import streamlit as st
from dashboard.config import APP_CONFIG

with st.container(horizontal=True, width="stretch", horizontal_alignment="center"):
    st.image("kochcloud/kochcloud_logo.svg", width=256)

st.title("Kochcloud für {}".format(st.user["name"]))

st.header("Dienste")

c1, c2 = st.columns(2, gap="small")

for i, link in enumerate(APP_CONFIG["services"]):
    c = c1 if i % 2 == 0 else c2
    label = "**{}**\n\n{}".format(link["title"], link["description"])
    c.link_button(label=label, url=link["url"], icon=link.get("icon", None), width="stretch")

st.header("Konfiguration")

c1, c2 = st.columns(2, gap="small")
c1.page_link("emailpasswords/email-passwords-page.py", label="Email-Passwörter verwalten", icon="📧", width="stretch")
c2.page_link("vpn/vpn-page.py", label="Kochcloud VPN konfigurieren", icon="🔒", width="stretch")