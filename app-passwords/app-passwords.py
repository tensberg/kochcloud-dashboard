import streamlit as st
from sqlalchemy.sql import text
import string
import secrets

# adapt numpy dataframe to postgresql, https://stackoverflow.com/a/56766135/1095318
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)

EMAIL_APP="dovecot"
EMAIL_HASH_ALGO="bf"

DATETIME_FORMAT="DD.MM.YYYY HH:mm"

conn = st.connection("postgresql", type="sql")

@st.dialog("Neues Passwort", dismissible=True)
def create_password_form():
    with st.form("create_password"):
        description_val = st.text_input("Beschreibung", placeholder="Thunderbird Android", max_chars=40)

        submitted = st.form_submit_button("Passwort erzeugen")
        if submitted:
            if not description_val:
                st.error("Bitte Beschreibung angeben")
            else:
                st.session_state["generated_password"] = create_password(description_val)
                st.rerun()

def create_password(description):
    password = generate_password()
    with conn.session as session:
        session.execute(text("INSERT INTO \"token\" (user_id,app,description,hash) VALUES (:user_id,:app,:description,CRYPT(:password, gen_salt(:hash_algo)))"), {
            "user_id": user_id,
            "app": EMAIL_APP,
            "description": description,
            "password": password,
            "hash_algo": EMAIL_HASH_ALGO
        })
        session.commit()
    return password

def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(16))

def upsert_loggedin_user():
    with conn.session as session:
        result = session.execute(text("""
                        INSERT INTO "user" (sub,email,last_login) VALUES (:sub,:email, NOW())
                        ON CONFLICT (sub) DO UPDATE SET email=:email, last_login=NOW()
                        RETURNING id;
                        """), {
                            "sub": st.user.sub,
                            "email": st.user.email
                        })
        session.commit()
        return result.one()[0]

@st.dialog("Passwort löschen", dismissible=True)
def confirm_delete_password(pw_id, description):
    st.write("Wollen Sie wirklich das Email-Passwort '{}' löschen?".format(description))

    with st.container(horizontal=True, width="content"):
        if st.button("Löschen"):
            delete_password(pw_id)
            st.rerun()

        if (st.button("Abbrechen")):
            st.rerun()

def delete_password(pw_id):
    with conn.session as session:
        result = session.execute(text("DELETE FROM \"token\" where id=:id"), { "id": pw_id })
        session.commit()
        print(result)

# main application

if not st.user.is_logged_in:
    st.login()

if 'user_id' not in st.session_state:
    user_id = upsert_loggedin_user()
    st.session_state['user_id'] = user_id
else:
    user_id = st.session_state['user_id']

st.title("Kochcloud Email für {}".format(st.user["name"]))

st.header("Email-Konfiguration")

generated_password = st.session_state.get("generated_password")

with st.container(horizontal=True, vertical_alignment="center", width="content"):
    st.write("Email-Adresse")
    st.code(st.user["email"])
with st.container(horizontal=True, vertical_alignment="center", width="content"):
    st.write("Passwort")
    if generated_password:
        st.code(generated_password)
        hide_password = st.button("Schließen")
        if hide_password:
            del st.session_state["generated_password"]
            st.rerun()
    else:
        new_password_button = st.button("Neues Passwort")
        if new_password_button:
            create_password_form()

st.header("Email-Passwörter")

df = conn.query("""
                SELECT t.id, t.description, t.created, t.last_used
                    FROM "token" t,"user" u 
                    WHERE t.user_id=u.id AND u.sub=:sub
                ORDER BY t.created
                """, ttl=0, params = { "sub": st.user["sub"]})

pw_table = st.dataframe(data=df, selection_mode="single-row", on_select="rerun",
             placeholder="-", column_config={
    0: None,
    "id": None,
    "description": "Beschreibung",
    "created": st.column_config.DatetimeColumn("Erstellt", format=DATETIME_FORMAT),
    "last_used": st.column_config.DatetimeColumn("Zuletzt verwendet", format=DATETIME_FORMAT)
})

pw_selected_row = pw_table.selection.rows[0] if pw_table.selection.rows else None

delete_password_button = st.button("Passwort löschen", disabled=(pw_selected_row==None))
if delete_password_button:
    confirm_delete_password(df.at[pw_selected_row, "id"], df.at[pw_selected_row, "description"])


