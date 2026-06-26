import tkinter as tk
import hashlib

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    _MYSQL_AVAILABLE = True
except ImportError:
    _MYSQL_AVAILABLE = False
    MySQLError = Exception

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",
    "database": "ghostbuster",
    "port":     3306,
}


def _get_connection():
    if not _MYSQL_AVAILABLE:
        raise ConnectionError("mysql-connector-python belum diinstall. "
                              "Jalankan: pip install mysql-connector-python")
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except MySQLError as e:
        raise ConnectionError(f"Gagal konek DB: {e}")


def _execute_query(query: str, params: tuple = (), fetch: bool = False):
    conn   = _get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.lastrowid
    except MySQLError as e:
        conn.rollback()
        raise RuntimeError(f"Query error: {e}")
    finally:
        cursor.close()
        conn.close()


def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def db_register(username: str, password: str) -> dict:
    existing = _execute_query(
        "SELECT id FROM users WHERE username=%s", (username,), fetch=True)
    if existing:
        return {"success": False, "message": "Username sudah digunakan."}
    if len(password) < 4:
        return {"success": False, "message": "Password minimal 4 karakter."}
    uid = _execute_query(
        "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
        (username, _hash_pw(password)))
    _execute_query("INSERT INTO game_progress (user_id) VALUES (%s)", (uid,))
    return {"success": True, "message": "Registrasi berhasil!", "user_id": uid}


def db_login(username: str, password: str) -> dict:
    rows = _execute_query(
        "SELECT id, username FROM users WHERE username=%s AND password_hash=%s",
        (username, _hash_pw(password)), fetch=True)
    if rows:
        return {"success": True, "user": rows[0]}
    return {"success": False, "message": "Username atau password salah."}
