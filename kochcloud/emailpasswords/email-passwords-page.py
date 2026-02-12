import streamlit as st
from dashboard.config import MOMENTJS_DATETIME_FORMAT, TZ_NAME
from emailpasswords.passwords import pw_create_password,pw_delete_password, pw_get_passwords_for_user

@st.dialog("Passwort erzeugen", dismissible=True)
def create_password_form():
    with st.form("create_password"):
        description_val = st.text_input("Beschreibung", placeholder="Thunderbird Android", max_chars=40)

        submitted = st.form_submit_button("Passwort erzeugen", icon=":material/add:")
        if submitted:
            if not description_val:
                st.error("Bitte Beschreibung angeben")
            else:
                st.session_state["generated_password"] = pw_create_password(description_val)
                st.rerun()


@st.dialog("Passwort löschen", dismissible=True)
def confirm_delete_password(pw_id, description):
    st.write("Wollen Sie wirklich das Email-Passwort '{}' löschen?".format(description))

    with st.container(horizontal=True, width="content"):
        if st.button("Löschen", icon=":material/delete:"):
            pw_delete_password(pw_id)
            st.rerun()

        if (st.button("Abbrechen", icon=":material/cancel:")):
            st.rerun()

# main application

st.title("Kochcloud Email für {}".format(st.user["name"]))

st.header("Email-Konfiguration")

generated_password = st.session_state.get("generated_password")

with st.container(horizontal=True, vertical_alignment="center"):
    col1, col2 = st.columns([1, 4], vertical_alignment="center")
    col1.write("Email-Adresse")
    col2.code(st.user["email"])
with st.container(horizontal=True, vertical_alignment="center"):
    col1, col2 = st.columns([1, 4], vertical_alignment="center")
    col1.write("Passwort")
    with col2.container(horizontal=True, vertical_alignment="center"):
        if generated_password:
            st.code(generated_password)
            hide_password = st.button("Schließen", icon=":material/close:")
            if hide_password:
                del st.session_state["generated_password"]
                st.rerun()
        else:
            new_password_button = col2.button("Passwort erzeugen", icon=":material/add:")
            if new_password_button:
                create_password_form()

st.header("Email-Passwörter")

stored_passwords = pw_get_passwords_for_user(st.user["sub"])

pw_table = st.dataframe(data=stored_passwords, selection_mode="single-row", on_select="rerun",
             placeholder="-", column_config={
    0: None,
    "id": None,
    "description": "Beschreibung",
    "created": st.column_config.DatetimeColumn("Erstellt", format=MOMENTJS_DATETIME_FORMAT, timezone=TZ_NAME),
    "last_used": st.column_config.DatetimeColumn("Zuletzt verwendet", format=MOMENTJS_DATETIME_FORMAT, timezone=TZ_NAME)
})

pw_selected_row = pw_table.selection.rows[0] if pw_table.selection.rows else None

delete_password_button = st.button("Passwort löschen", icon=":material/delete:", disabled=(pw_selected_row==None))
if delete_password_button:
    pw_id = stored_passwords.at[pw_selected_row, "id"]
    description = stored_passwords.at[pw_selected_row, "description"]
    confirm_delete_password(pw_id, description)

