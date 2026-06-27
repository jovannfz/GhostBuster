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
                row=0, column=col, padx=1, pady
        medals = ["🥇", "🥈", "🥉"] + ["  "] * 7
        for i, widgets in enumerate(self._rows):
            if i < len(data):
                r   = data[i]
                rank = medals[i] if i < 3 else str(i + 1)
                vals = [rank, r["username"], f"{r['score']:,}",
                        str(r["level_reached"]), r["tanggal"]]
                fg = (self.C_ACC if i == 0 else "#c0c0c0" if i == 1 else
                      "#cd7f32" if i == 2 else self.C_TXT)
            else:
                vals = [str(i + 1), "—", "—", "—", "—"]
                fg   = self.C_MUT
            for lbl, val in zip(widgets, vals):
                lbl.config(text=val, fg=fg)

    def on_show(self):
        self._load() 

# ══════════════════════════════════════════════════════════════════
#  SCREEN — PENGATURAN & PROFIL
# ══════════════════════════════════════════════════════════════════ 

class SettingsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="⚙  PENGATURAN",
                 font=("Courier New", 36, "bold"),
                 bg=self.BG, fg=self.C_PRI).grid(row=0, column=0, pady=(60, 24)) 