import streamlit as st

# authentication and login

if not st.user.is_logged_in:
    st.login()
    st.write("Bitte melden Sie sich an, um auf das Kochcloud Dashboard zuzugreifen.")
    st.stop() # the script will be re-run after login

# general page setup

st.set_page_config("Kochcloud", ":cloud:")
st.logo("kochcloud-dashboard/kochcloud_logo.svg", size="large")

# page definitions

pg = st.navigation([
    st.Page("dashboard.py", title="☁️ Übersicht"), 
    st.Page("email-passwords.py", title="📧 Email-Passwörter"),
    st.Page("vpn.py", title="🔒 Kochcloud VPN"),
    ])
pg.run()
