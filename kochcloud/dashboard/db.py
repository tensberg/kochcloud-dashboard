import streamlit as st
from sqlalchemy.sql import text

DB_CONNECTION = st.connection("postgresql", type="sql")

# functions
def db_upsert_loggedin_user():
    with DB_CONNECTION.session as session:
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

def db_user_id():
    if 'user_id' not in st.session_state:
        user_id = db_upsert_loggedin_user()
        st.session_state['user_id'] = user_id
    else:
        user_id = st.session_state['user_id']
    return user_id

# main
# adapt numpy dataframe to postgresql, https://stackoverflow.com/a/56766135/1095318
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)

DB_USER_ID=db_user_id()
