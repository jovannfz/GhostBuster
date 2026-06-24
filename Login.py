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