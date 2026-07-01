import tkinter as tk
from tkinter import messagebox
from jovan_db_auth   import AuthScreen, db_get_leaderboard, db_get_progress
from ozy_game_screen import GameScreen, BaseScreen

# ══════════════════════════════════════════════════════════════════
#  SCREEN — MENU UTAMA
# ══════════════════════════════════════════════════════════════════

class MenuScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="👻  🌙  👻  🌙  👻",
                 font=("Courier New", 18), bg=self.BG, fg="#334").grid(row=0, column=0, pady=(60, 0))

        tk.Label(self, text="GHOSTBUSTERS",
                 font=("Courier New", 54, "bold"),
                 bg=self.BG, fg=self.C_PRI).grid(row=1, column=0, pady=(8, 2))

        tk.Label(self, text="Bust Ghosts. Save the Night.",
                 font=("Courier New", 17), bg=self.BG, fg=self.C_ACC).grid(row=2, column=0, pady=(0, 36))

        self._welcome = tk.StringVar(value="Selamat datang!")
        tk.Label(self, textvariable=self._welcome,
                 font=self.F_HEAD, bg=self.BG, fg=self.C_TXT).grid(row=3, column=0, pady=(0, 26))

        btns = [
            ("▶  MULAI GAME",   self.C_PRI, "#000",     lambda: self.controller.show("GameScreen")),
            ("🏆  LEADERBOARD", self.C_ACC, "#000",     lambda: self.controller.show("LeaderboardScreen")),
            ("⚙  PENGATURAN",  "#1e4d2b",  self.C_TXT, lambda: self.controller.show("SettingsScreen")),
            ("🚪  KELUAR",      self.C_DNG, "#fff",     self.controller.quit),
        ]
        for i, (text, bg, fg, cmd) in enumerate(btns):
            tk.Button(self, text=text, font=self.F_HEAD, width=30,
                      pady=13, bg=bg, fg=fg, relief="flat", cursor="hand2",
                      command=cmd).grid(row=4 + i, column=0, pady=8)

        tk.Label(self, text="👻  💀  👻  💀  👻",
                 font=("Courier New", 16), bg=self.BG, fg="#222").grid(row=8, column=0, pady=(28, 0))

    def on_show(self):
        u = self.controller.current_user
        if u:
            self._welcome.config(value=f"Halo, {u['username']}! 👋")

# ══════════════════════════════════════════════════════════════════
#  SCREEN — GAME OVER / VICTORY
# ══════════════════════════════════════════════════════════════════

class GameOverScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._score   = 0
        self._level   = 1
        self._victory = False
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        self._icon = tk.Label(self, text="💀", font=("Arial", 80), bg=self.BG)
        self._icon.grid(row=0, column=0, pady=(90, 0))

        self._title = tk.Label(self, text="GAME OVER",
                               font=("Courier New", 44, "bold"),
                               bg=self.BG, fg=self.C_DNG)
        self._title.grid(row=1, column=0, pady=(8, 28))

        card = tk.Frame(self, bg=self.C_CARD, padx=60, pady=32)
        card.grid(row=2, column=0)

        self._sc_var = tk.StringVar(value="Skor Akhir: 0")
        self._lv_var = tk.StringVar(value="Level Tercapai: 1 / 3")

        tk.Label(card, textvariable=self._sc_var,
                 font=("Courier New", 26, "bold"),
                 bg=self.C_CARD, fg=self.C_ACC).pack(pady=4)
        tk.Label(card, textvariable=self._lv_var,
                 font=self.F_HEAD, bg=self.C_CARD, fg=self.C_TXT).pack(pady=4)

        btn = dict(font=self.F_HEAD, width=28, pady=12, relief="flat", cursor="hand2")

        tk.Button(self, text="🔄  MAIN LAGI",    bg=self.C_PRI, fg="#000",
                  command=lambda: self.controller.show("GameScreen"), **btn).grid(
            row=3, column=0, pady=(36, 8))
        tk.Button(self, text="🏆  LEADERBOARD",  bg=self.C_ACC, fg="#000",
                  command=lambda: self.controller.show("LeaderboardScreen"), **btn).grid(
            row=4, column=0, pady=5)
        tk.Button(self, text="🏠  MENU UTAMA",   bg="#1e4d2b", fg=self.C_TXT,
                  command=lambda: self.controller.show("MenuScreen"), **btn).grid(
            row=5, column=0, pady=5)

    def set_result(self, score: int, level: int, victory: bool):
        self._score   = score
        self._level   = level
        self._victory = victory

    def on_show(self):
        if self._victory:
            self._icon.config(text="🏆")
            self._title.config(text="YOU WIN! 🎉", fg=self.C_ACC)
        else:
            self._icon.config(text="💀")
            self._title.config(text="GAME OVER", fg=self.C_DNG)
        self._sc_var.set(f"Skor Akhir: {self._score:,}")
        self._lv_var.set(f"Level Tercapai: {self._level} / 3")

# ══════════════════════════════════════════════════════════════════
#  SCREEN — LEADERBOARD
# ══════════════════════════════════════════════════════════════════

class LeaderboardScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="🏆  LEADERBOARD",
                 font=("Courier New", 36, "bold"),
                 bg=self.BG, fg=self.C_ACC).grid(row=0, column=0, pady=(60, 6))
        tk.Label(self, text="Top 10 Ghost Buster Terbaik",
                 font=self.F_BODY, bg=self.BG, fg=self.C_MUT).grid(row=1, column=0, pady=(0, 16))

        tbl  = tk.Frame(self, bg=self.C_CARD)
        tbl.grid(row=2, column=0, padx=80)

        headers = ["#",  "Username", "Skor", "Level", "Tanggal"]
        col_w   = [4,    18,          12,      8,       18]
        for col, (h, w) in enumerate(zip(headers, col_w)):
            tk.Label(tbl, text=h, font=("Courier New", 11, "bold"),
                     bg="#1e3a5c", fg=self.C_ACC, width=w, pady=5).grid(
                row=0, column=col, padx=1, pady=(0, 2), sticky="ew")

        self._rows = []
        for r in range(10):
            row_w = []
            bg = self.C_CARD if r % 2 == 0 else "#0a1528"
            for col, w in enumerate(col_w):
                lbl = tk.Label(tbl, text="—", font=self.F_SM,
                               bg=bg, fg=self.C_TXT, width=w, pady=4)
                lbl.grid(row=r + 1, column=col, padx=1, pady=1, sticky="ew")
                row_w.append(lbl)
            self._rows.append(row_w)         