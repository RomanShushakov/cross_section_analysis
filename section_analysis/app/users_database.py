import os
import asyncpg

from fastapi import HTTPException
from passlib.context import CryptContext

from app.database import POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB_ADDR, POSTGRES_DB

# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "fastapi_users_pass_test")
# POSTGRES_USER = os.getenv("POSTGRES_USER", "fastapi_users_user_test")
# POSTGRES_DB_ADDR = os.getenv("POSTGRES_DB_ADDR", "localhost")
# POSTGRES_DB = os.getenv("POSTGRES_DB", "fastapi_users_db_test")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)


async def _create_table():
    conn = await asyncpg.connect(
        f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}"
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id serial PRIMARY KEY,
            full_name text,
            email text,
            username text,
            hashed_password text,
            disabled bool,
            is_superuser bool
         )
        """
    )
    await conn.close()


async def extract_users_from_db():
    await _create_table()
    conn = await asyncpg.connect(
        f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}")
    all_user_records = await conn.fetch("SELECT * FROM users",)
    await conn.close()
    all_users = dict()
    for record in all_user_records:
        full_name, email, username = record[1], record[2], record[3]
        hashed_password, disabled, is_superuser = record[4], record[5], record[6]
        all_users[username] = {"full_name": full_name, "email": email, "username": username,
                               "hashed_password": hashed_password, "disabled": disabled, "is_superuser": is_superuser}
    return all_users


async def user_email_check(user):
    conn = await asyncpg.connect(f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}")
    user_record_with_same_email = await conn.fetch(
        "SELECT * FROM users WHERE email = $1",
        user.email
        )
    await conn.close()
    if not user_record_with_same_email:
        return True
    return False


async def user_username_check(user):
    conn = await asyncpg.connect(f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}")
    user_record_with_same_username = await conn.fetch(
        "SELECT * FROM users WHERE username = $1",
        user.username
        )
    await conn.close()
    if not user_record_with_same_username:
        return True
    return False


async def add_user_into_db(user):
    await _create_table()
    email_check_passed = await user_email_check(user=user)
    if not email_check_passed:
        raise HTTPException(status_code=400, detail="The entered email is already in use.")
    username_check_passed = await user_username_check(user=user)
    if not username_check_passed:
        raise HTTPException(status_code=400, detail="The entered username is already in use.")
    conn = await asyncpg.connect(f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DB_ADDR}/{POSTGRES_DB}")
    await conn.execute(
        """
        INSERT INTO users(
            full_name, email, username, hashed_password, disabled, is_superuser) VALUES(
                $1, $2, $3, $4, $5, $6)""",
        user.full_name,
        user.email,
        user.username,
        get_password_hash(user.password),
        user.disabled,
        user.is_superuser,
    )
    await conn.close()
    return "Registration was successfully completed."
