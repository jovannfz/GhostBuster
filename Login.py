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

def db_save_score(user_id: int, score: int, level_reached: int):
    _execute_query(
        "INSERT INTO scores (user_id, score, level_reached) VALUES (%s,%s,%s)",
        (user_id, score, level_reached))
    _execute_query(
        """INSERT INTO game_progress (user_id, skor_terbaik, level_tercapai)
           VALUES (%s,%s,%s)
           ON DUPLICATE KEY UPDATE
             skor_terbaik   = IF(skor_terbaik < %s,  %s, skor_terbaik),
             level_tercapai = IF(level_tercapai < %s, %s, level_tercapai)""",
        (user_id, score, level_reached, score, score, level_reached, level_reached))


def db_get_leaderboard(limit: int = 10) -> list:
    return _execute_query(
        """SELECT u.username, s.score, s.level_reached,
                  DATE_FORMAT(s.waktu_bermain,'%%d/%%m/%%Y %%H:%%i') AS tanggal
           FROM scores s JOIN users u ON s.user_id=u.id
           ORDER BY s.score DESC LIMIT %s""",
        (limit,), fetch=True)


def db_get_progress(user_id: int):
    rows = _execute_query(
        "SELECT * FROM game_progress WHERE user_id=%s", (user_id,), fetch=True)
    return rows[0] if rows else None
