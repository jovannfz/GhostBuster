import tkinter as tk

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
    "database": "ghostbusters_db",
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


def db_register(username: str, password: str) -> dict:
    errors = []
    existing = _execute_query(
        "SELECT id FROM users WHERE username=%s", (username,), fetch=True)
    if existing:
        errors.append("Username sudah digunakan.")
    if len(password) < 4:
        errors.append("Password harus terdiri dari 4 karakter.")
    if errors:
        return {"success": False, "message": " ".join(errors)}
    uid = _execute_query(
        "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
        (username, password))
    _execute_query("INSERT INTO game_progress (user_id) VALUES (%s)", (uid,))
    return {"success": True, "message": "Registrasi berhasil!", "user_id": uid}


def db_login(username: str, password: str) -> dict:
    rows = _execute_query(
        "SELECT id, username FROM users WHERE username=%s AND password_hash=%s",
        (username, password), fetch=True)
    if rows:
        return {"success": True, "user": rows[0]}
    return {"success": False, "message": "Username atau password salah."}

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
        """SELECT u.username, s.score
           FROM scores s JOIN users u ON s.user_id=u.id
           ORDER BY s.score DESC LIMIT %s""",
        (limit,), fetch=True)


def db_get_progress(user_id: int):
    rows = _execute_query(
        "SELECT * FROM game_progress WHERE user_id=%s", (user_id,), fetch=True)
    return rows[0] if rows else None

class AuthScreen(tk.Frame):
    BG      = "#0a0f1e"
    C_PRI   = "#a8d8ff"
    C_ACC   = "#f9d423"
    C_DNG   = "#ff416c"
    C_TXT   = "#e8e8e8"
    C_MUT   = "#666"
    C_CARD  = "#0d1a2e"
    F_HEAD  = ("Courier New", 20, "bold")
    F_BODY  = ("Courier New", 15)
    F_SM    = ("Courier New", 12)

    def __init__(self, parent, controller):
        super().__init__(parent, bg=self.BG)
        self.controller = controller
        self._mode = "login"
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="👻  GHOSTBUSTERS  👻",
                 font=("Courier New", 26, "bold"),
                 bg=self.BG, fg=self.C_PRI).grid(row=0, column=0, pady=(50, 4))

        tk.Label(self, text="Bust ghosts. Save the night.",
                 font=("Courier New", 14), bg=self.BG, fg=self.C_MUT).grid(
            row=1, column=0, pady=(0, 18))

        card = tk.Frame(self, bg=self.C_CARD, padx=36, pady=20)
        card.grid(row=2, column=0)

        self._title = tk.Label(card, text="LOGIN",
                               font=("Courier New", 18, "bold"),
                               bg=self.C_CARD, fg=self.C_ACC)
        self._title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        tk.Label(card, text="Username", font=self.F_SM,
                 bg=self.C_CARD, fg=self.C_TXT).grid(
            row=1, column=0, sticky="w", pady=2)

        self._pw_lbl = tk.Label(card, text="Password", font=self.F_SM,
                                bg=self.C_CARD, fg=self.C_TXT)
        self._pw_lbl.grid(row=3, column=0, sticky="w", pady=2)

        entry_cfg = dict(font=self.F_SM, width=26, bg="#060f1a",
                         fg=self.C_TXT, insertbackground="white",
                         relief="flat", highlightthickness=1,
                         highlightbackground=self.C_PRI)

        self._user_var = tk.StringVar()
        self._pw_var   = tk.StringVar()
        self._cf_var   = tk.StringVar()

        tk.Entry(card, textvariable=self._user_var, **entry_cfg).grid(
            row=2, column=0, columnspan=2, ipady=4, pady=(0, 5))
        self._pw_entry = tk.Entry(card, textvariable=self._pw_var, show="•", **entry_cfg)
        self._pw_entry.grid(row=4, column=0, columnspan=2, ipady=4, pady=(0, 5))

        self._cf_lbl   = tk.Label(card, text="Konfirmasi Password",
                                  font=self.F_SM, bg=self.C_CARD, fg=self.C_TXT)
        self._cf_entry = tk.Entry(card, textvariable=self._cf_var, show="•", **entry_cfg)

        self._btn = tk.Button(card, text="MASUK",
                              font=("Courier New", 15, "bold"), bg=self.C_PRI, fg="#000",
                              relief="flat", cursor="hand2", width=22, pady=6,
                              command=self._action)
        self._btn.grid(row=7, column=0, columnspan=2, pady=(10, 6))

        self._toggle = tk.Label(card, text="Belum punya akun? Daftar di sini",
                                font=self.F_SM, bg=self.C_CARD,
                                fg=self.C_ACC, cursor="hand2")
        self._toggle.grid(row=8, column=0, columnspan=2)
        self._toggle.bind("<Button-1>", lambda e: self._switch())

        self._msg = tk.StringVar()
        tk.Label(self, textvariable=self._msg, font=self.F_SM,
                 bg=self.BG, fg=self.C_DNG, wraplength=500).grid(
            row=3, column=0, pady=(8, 0))

    def _switch(self):
        self._msg.set("")
        if self._mode == "login":
            self._mode = "register"
            self._title.config(text="REGISTER")
            self._btn.config(text="DAFTAR")
            self._toggle.config(text="Sudah punya akun? Login di sini")
            self._pw_lbl.config(text="Password (harus 4 karakter)")
            self._cf_lbl.grid(row=5, column=0, sticky="w", pady=3)
            self._cf_entry.grid(row=6, column=0, columnspan=2, ipady=6, pady=(0, 8))
        else:
            self._mode = "login"
            self._title.config(text="LOGIN")
            self._btn.config(text="MASUK")
            self._toggle.config(text="Belum punya akun? Daftar di sini")
            self._pw_lbl.config(text="Password")
            self._cf_lbl.grid_remove()
            self._cf_entry.grid_remove()

    def _action(self):
        u = self._user_var.get().strip()
        p = self._pw_var.get().strip()
        if not u or not p:
            self._msg.set("⚠ Username & password wajib diisi."); return

        try:
            if self._mode == "register":
                c = self._cf_var.get().strip()
                if p != c:
                    self._msg.set("⚠ Password tidak cocok."); return
                res = db_register(u, p)
            else:
                res = db_login(u, p)
        except Exception as e:
            self._msg.set(f"⚠ Koneksi DB gagal: {e}"); return

        if res["success"]:
            self._msg.set("")
            if self._mode == "register":
                user = {"id": res.get("user_id"), "username": u}
            else:
                user = res.get("user") or {"id": None, "username": u}
            self.controller.set_user(user)
            self.controller.show("MenuScreen")
        else:
            self._msg.set(f"⚠ {res['message']}")

    def on_show(self):
        self._user_var.set(""); self._pw_var.set(""); self._cf_var.set("")
        self._msg.set("")
        if self._mode != "login": self._switch()