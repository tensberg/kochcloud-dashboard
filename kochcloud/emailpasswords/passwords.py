import string
import secrets
from sqlalchemy.sql import text
from dashboard.db import DB_USER_ID
from dashboard.db import DB_CONNECTION as conn

EMAIL_APP="dovecot"
EMAIL_HASH_ALGO="bf"

PASSWORD_LENGTH=20

def pw_get_passwords_for_user(user_sub):
    return conn.query("""
                SELECT t.id, t.description, t.created, t.last_used
                    FROM "app_token" t,"user" u 
                    WHERE t.user_id=u.id AND u.sub=:sub
                ORDER BY t.created
                """, ttl=0, params = { "sub": user_sub})


def pw_create_password(description):
    password = generate_password()
    with conn.session as session:
        session.execute(text("INSERT INTO \"app_token\" (user_id,app,description,hash) VALUES (:user_id,:app,:description,CRYPT(:password, gen_salt(:hash_algo)))"), {
            "user_id": DB_USER_ID,
            "app": EMAIL_APP,
            "description": description,
            "password": password,
            "hash_algo": EMAIL_HASH_ALGO
        })
        session.commit()
    return password

def pw_delete_password(pw_id):
    with conn.session as session:
        result = session.execute(text("DELETE FROM \"app_token\" where id=:id"), { "id": pw_id })
        session.commit()
        print(result)

def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(PASSWORD_LENGTH))
