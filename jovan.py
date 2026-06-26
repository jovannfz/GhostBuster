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

LEVEL_CFG = {
    1: {"nama": "Easy",   "tema": "Hutan Siang",   "kecepatan": 2.5, "timer": 120, "hantu": 4,  "mult": 1.0},
    2: {"nama": "Medium", "tema": "Kuburan Malam", "kecepatan": 4.0, "timer": 80,  "hantu": 7,  "mult": 1.5},
    3: {"nama": "Hard",   "tema": "Kastil Iblis",  "kecepatan": 6.5, "timer": 50,  "hantu": 11, "mult": 2.0},
}

THEME = {
    1: {"sky": "#1a3a6c", "ground": "#2d5a1b", "platform": "#5a3a1a", "grass": "#3a8a2a", "label": "#a8ff78", "moon": "#c8c8c8"},
    2: {"sky": "#0d1a2e", "ground": "#1a1a2e", "platform": "#3a2a0a", "grass": "#1a3a1a", "label": "#f9d423", "moon": "#888899"},
    3: {"sky": "#0a0a1e", "ground": "#1a0a0a", "platform": "#2a0a0a", "grass": "#3a0a0a", "label": "#ff416c", "moon": "#665566"},
}

GHOST_TYPES = [
    {"color": "#e8e8f0", "speed_mult": 1.0, "hp": 1, "score": 100, "name": "Normal"},
    {"color": "#f8c0d8", "speed_mult": 1.6, "hp": 1, "score": 80,  "name": "Cepat"},
    {"color": "#c0b0f0", "speed_mult": 0.6, "hp": 3, "score": 200, "name": "Kuat"},
]

GROUND_Y = 380   # y tanah utama di canvas
P_FLOOR  = 346   # y pemain saat berdiri di tanah (GROUND_Y - player.H)


class LevelManager:
    def __init__(self):
        self.current = 1
        self.max     = 3

    def cfg(self):    return LEVEL_CFG[self.current]
    def theme(self):  return THEME[self.current]
    def is_last(self): return self.current == self.max
    def reset(self):   self.current = 1

    def next(self) -> bool:
        if self.current < self.max:
            self.current += 1
            return True
        return False

class ScoreManager:
    BASE_COIN = 50
    TIME_MULT = 5

    def __init__(self, mult=1.0):
        self.mult  = mult
        self.total = 0

    def ghost_kill(self, base=100):
        g = int(base * self.mult); self.total += g; return g

    def coin(self):
        g = int(self.BASE_COIN * self.mult); self.total += g; return g

    def time_bonus(self, secs):
        b = int(secs * self.TIME_MULT * self.mult); self.total += b; return b

    def penalty(self, amt=50):
        self.total = max(0, self.total - amt)