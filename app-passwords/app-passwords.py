import streamlit as st

EMAIL_APP="dovecot"

@st.dialog("Neues Passwort", dismissible=True)
def create_password_form():
    with st.form("create_password"):
        description_val = st.text_input("Beschreibung", placeholder="Thunderbird Android", max_chars=40)
        limit_validity_val = st.checkbox("Gültigkeit begrenzen")
        validity_val = st.date_input("Gültig bis", min_value="today", format="DD.MM.YYYY")

        submitted = st.form_submit_button("Passwort erzeugen")
        if submitted:
            # TODO: passwort anlegen
            st.rerun()

# main application

if not st.user.is_logged_in:
    st.login()

conn = st.connection("postgresql", type="sql")

st.title("App Passwörter für {}".format(st.user["name"]))

st.header("Email-Passwörter für {}".format(st.user["email"]))

df = conn.query("""
                SELECT t.id, t.description, t.expires, t.created 
                    FROM token t,user u 
                    WHERE t.user_id=u.id AND u.sub=:sub
                ORDER BY t.created
                """, ttl=0, params = { "sub": st.user["sub"]})

if st.button("Neues Passwort"):
    create_password_form()
