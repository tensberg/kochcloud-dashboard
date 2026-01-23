import streamlit as st
from config import APP_CONFIG

with st.container(horizontal=True, width="stretch", horizontal_alignment="center"):
    st.image("static/kochcloud_logo.webp", width=256)

st.title("Kochcloud für {}".format(st.user["name"]))

st.header("Dienste")

c1, c2 = st.columns(2, gap="small")

for i, link in enumerate(APP_CONFIG["services"]):
    c = c1 if i % 2 == 0 else c2
    label = "**{}**\n\n{}".format(link["title"], link["description"])
    c.link_button(label=label, url=link["url"], icon=link.get("icon", None), width="stretch")

st.header("Konfiguration")

with st.container(horizontal=True, width="stretch"):
    st.page_link("email-passwords.py", label="Email-Passwörter verwalten", icon="📧", width="stretch")